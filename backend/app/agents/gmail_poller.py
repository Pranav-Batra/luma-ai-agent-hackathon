"""
THIS IS THE PUBLISHER(I.E. NEW YORK TIMES) RESPONDING TO A AD PITCH REQUEST
Gmail Reply Poller
Polls Gmail inbox every 30s for replies to pitch emails.
Matches replies to outreach_logs via subject line / In-Reply-To header.
Claude classifies intent → approved / counter / rejected
→ fires creative pipeline or counter-offer logic
"""

import os
from datetime import timedelta
import json
import asyncio
import imaplib
import email
import email.header
from email.policy import default as email_default_policy
from datetime import datetime, timezone
import httpx
import re
from app.agents.creative import run_approved_pipeline
from app.agents.helper import extract_json

import anthropic
from supabase import Client

OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

GMAIL_USER = os.environ.get("GMAIL_USER")           # your.email@gmail.com
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")  # 16-char app password
POLL_INTERVAL = int(os.environ.get("REPLY_POLL_INTERVAL", 30))  # seconds

INTENT_SYSTEM_PROMPT = """
You are classifying a publisher's email reply to an ad placement pitch.
Respond with ONLY a JSON object, no markdown, no explanation:
{
  "intent": "approved" | "rejected" | "counter",
  "counter_amount": <integer dollars or null>,
  "summary": "<one sentence describing the reply>"
}
"""


# ── Email parsing ─────────────────────────────────────────────────────────────

def _decode_header(value: str) -> str:
    """Decode encoded email headers like =?utf-8?q?...?="""
    if not value:
        return ""
    parts = email.header.decode_header(value)
    decoded = []
    for part, charset in parts:
        if isinstance(part, bytes):
            decoded.append(part.decode(charset or "utf-8", errors="replace"))
        else:
            decoded.append(part)
    return "".join(decoded)


def _extract_body(msg) -> str:
    """Extract plain text body from email message."""
    if msg.is_multipart():
        for part in msg.walk():
            ct = part.get_content_type()
            cd = str(part.get("Content-Disposition", ""))
            if ct == "text/plain" and "attachment" not in cd:
                charset = part.get_content_charset() or "utf-8"
                return part.get_payload(decode=True).decode(charset, errors="replace")
    else:
        charset = msg.get_content_charset() or "utf-8"
        return msg.get_payload(decode=True).decode(charset, errors="replace")
    return ""


def _fetch_unseen_emails(gmail_user: str, app_password: str) -> list[dict]:
    """Connect to Gmail via IMAP and fetch unseen emails."""
    emails = []
    try:
        with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
            mail.login(gmail_user, app_password)
            mail.select("inbox")

            since = (datetime.now() - timedelta(days=7)).strftime("%d-%b-%Y")
            _, message_ids = mail.search(None, f'(UNSEEN SINCE {since})')
            if not message_ids[0]:
                return []

            for mid in message_ids[0].split():
                _, msg_data = mail.fetch(mid, "(RFC822)")
                raw = msg_data[0][1]
                msg = email.message_from_bytes(raw, policy=email_default_policy)

                emails.append({
                    "imap_id": mid.decode(),
                    "from": _decode_header(msg.get("From", "")),
                    "subject": _decode_header(msg.get("Subject", "")),
                    "in_reply_to": msg.get("In-Reply-To", "").strip().strip("<>"),
                    "message_id": msg.get("Message-ID", "").strip().strip("<>"),
                    "body": _extract_body(msg),
                    "date": msg.get("Date", ""),
                })
    except Exception as e:
        print(f"[poller] IMAP error: {e}")
    return emails


def _mark_as_read(gmail_user: str, app_password: str, imap_id: str) -> None:
    """Mark an email as read so we don't process it again."""
    try:
        with imaplib.IMAP4_SSL("imap.gmail.com") as mail:
            mail.login(gmail_user, app_password)
            mail.select("inbox")
            mail.store(imap_id, "+FLAGS", "\\Seen")
    except Exception as e:
        print(f"[poller] Failed to mark email {imap_id} as read: {e}")


# ── DB helpers ────────────────────────────────────────────────────────────────

def _find_outreach_by_subject(sb: Client, subject: str) -> dict | None:
    """
    Match a reply to an outreach log by subject line.
    Strips Re: prefix and matches against stored email_subject.
    """
    clean = subject.strip()
    for prefix in ["Re: ", "RE: ", "re: ", "Fwd: ", "FWD: "]:
        if clean.startswith(prefix):
            clean = clean[len(prefix):]
            break

    r = sb.table("outreach_logs") \
        .select("*") \
        .ilike("email_subject", f"%{clean}%") \
        .eq("status", "sent") \
        .limit(1) \
        .execute()
    return r.data[0] if r.data else None


def _find_outreach_by_message_id(sb: Client, message_id: str) -> dict | None:
    """Match reply via In-Reply-To header against stored resend/smtp message ID."""
    if not message_id:
        return None
    r = sb.table("outreach_logs") \
        .select("*") \
        .eq("resend_id", message_id) \
        .limit(1) \
        .execute()
    return r.data[0] if r.data else None


def _update_outreach(sb: Client, outreach_id: str, intent: str,
                     reply_raw: str, counter_amount: int | None) -> None:
    sb.table("outreach_logs").update({
        "status": intent,
        "reply_raw": reply_raw[:5000],
        "reply_intent": intent,
        "counter_amount": counter_amount,
        "replied_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", outreach_id).execute()


def _log_event(sb: Client, campaign_id: str, event_type: str,
               message: str, metadata: dict) -> None:
    sb.table("agent_events").insert({
        "campaign_id": campaign_id,
        "event_type": event_type,
        "message": message,
        "metadata": metadata,
    }).execute()


# ── Intent classification ─────────────────────────────────────────────────────

async def _classify_intent(body: str) -> dict:
     async with httpx.AsyncClient() as client:
        res = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-3.5-haiku",  # or newer if available
                "messages": [
                    {"role": "system", "content": INTENT_SYSTEM_PROMPT},
                    {"role": "user", "content": body[:2000]},
                ],
                "max_tokens": 500,
            },
        )

        data = res.json()

    # Debug if needed
        if "error" in data:
            raise RuntimeError(f"OpenRouter error: {data['error']}")

        text = data["choices"][0]["message"]["content"].strip()
        print("MODEL TEXT:", text)
        return extract_json(text)
     """Call Claude to classify reply intent."""
    # try:
    #     msg = await claude.messages.create(
    #         model="claude-sonnet-4-20250514",
    #         max_tokens=200,
    #         system=INTENT_SYSTEM_PROMPT,
    #         messages=[{"role": "user", "content": body[:2000]}],
    #     )
    #     return json.loads(msg.content[0].text.strip())
    # except Exception as e:
    #     print(f"[poller] Classification error: {e}")
    #     return {"intent": "unknown", "counter_amount": None, "summary": str(e)}


# ── Next step routing ─────────────────────────────────────────────────────────

async def _handle_approved(sb: Client, outreach: dict) -> None:
    """Fire creative pipeline when publisher approves."""
    print(f"[poller] ✅ Approved! Campaign {outreach['campaign_id']} — triggering creative pipeline")
    _log_event(
        sb, outreach["campaign_id"], "approved",
        f"Publisher approved the deal — generating creative now",
        {"outreach_id": outreach["id"], "offer_amount": outreach["offer_amount"]},
    )
    await run_approved_pipeline(sb, outreach)
    # TODO: import and call creative pipeline
    # from app.agents.creative import run_creative_pipeline
    # await run_creative_pipeline(sb, outreach["id"])


async def _handle_counter(sb: Client, outreach: dict, counter_amount: int, summary: str) -> None:
    """Claude generates a counter-counter offer and sends it."""
    print(f"[poller] 🔄 Counter offer ${counter_amount} — generating response")
    _log_event(
        sb, outreach["campaign_id"], "counter",
        f"Publisher countered at ${counter_amount} — {summary}",
        {"outreach_id": outreach["id"], "counter_amount": counter_amount},
    )
    # TODO: generate and send counter-counter email
    # from app.agents.outreach import send_counter_offer
    # await send_counter_offer(sb, outreach["id"], counter_amount)


async def _handle_rejected(sb: Client, outreach: dict, summary: str) -> None:
    """Log rejection and move to next publisher."""
    print(f"[poller] ❌ Rejected — {summary}")
    _log_event(
        sb, outreach["campaign_id"], "rejected",
        f"Publisher rejected the pitch — {summary}",
        {"outreach_id": outreach["id"]},
    )
    # TODO: trigger outreach to next publisher
    # from app.agents.outreach import run_outreach_for_campaign
    # await run_outreach_for_campaign(sb, outreach["campaign_id"], max_publishers=1)


# ── Main poll loop ────────────────────────────────────────────────────────────

async def process_email(sb: Client, em: dict) -> None:
    """Process a single inbound email — match, classify, route."""
    print(f"[poller] Processing reply from {em['from']} — subject: {em['subject']}")

    # Try to match to an outreach log
    outreach = await asyncio.to_thread(_find_outreach_by_message_id, sb, em["in_reply_to"])
    if not outreach:
        outreach = await asyncio.to_thread(_find_outreach_by_subject, sb, em["subject"])

    if not outreach:
        print(f"[poller] No matching outreach found for: {em['subject']} — skipping")
        return

    # Classify intent
    classification = await _classify_intent(em["body"])
    intent = classification.get("intent", "unknown")
    counter_amount = classification.get("counter_amount")
    summary = classification.get("summary", "")

    print(f"[poller] Intent: {intent} | Summary: {summary}")

    # Update DB
    await asyncio.to_thread(
        _update_outreach, sb, outreach["id"], intent, em["body"], counter_amount
    )

    # Route to next step
    if intent == "approved":
        await _handle_approved(sb, outreach)
    elif intent == "counter":
        await _handle_counter(sb, outreach, counter_amount or 0, summary)
    elif intent == "rejected":
        await _handle_rejected(sb, outreach, summary)
    else:
        print(f"[poller] Unknown intent '{intent}' — logged but no action taken")


async def poll_once(sb: Client) -> None:
    """Single poll cycle — fetch unseen emails and process each one."""
    emails = await asyncio.to_thread(_fetch_unseen_emails, GMAIL_USER, GMAIL_APP_PASSWORD)

    if not emails:
        print(f"[poller] No new emails")
        return

    print(f"[poller] Found {len(emails)} new email(s)")
    for em in emails:
        await process_email(sb, em)
        # Mark as read so we don't process it again next cycle
        await asyncio.to_thread(_mark_as_read, GMAIL_USER, GMAIL_APP_PASSWORD, em["imap_id"])


async def start_poller(sb: Client) -> None:
    """
    Main poller loop. Run this as a background task when the server starts.
    Checks Gmail every POLL_INTERVAL seconds.
    """
    print(f"[poller] Started — checking Gmail every {POLL_INTERVAL}s")
    while True:
        try:
            await poll_once(sb)
        except Exception as e:
            print(f"[poller] Unexpected error: {e}")
        await asyncio.sleep(POLL_INTERVAL)