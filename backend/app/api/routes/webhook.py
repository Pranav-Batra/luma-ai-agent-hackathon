"""
Webhook handler for inbound publisher replies via Resend.
Flow: email arrives → Resend POSTs here → Claude classifies intent
      → approved: trigger creative pipeline
      → counter: Claude generates counter-counter and sends it
      → rejected: log and move to next publisher
"""
import asyncio
import json
import os
from datetime import datetime, timezone

import anthropic
from fastapi import APIRouter, Depends, HTTPException, Request
from supabase import Client

from app.core.database import get_supabase

router = APIRouter()

claude = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))

INTENT_SYSTEM_PROMPT = """
You are classifying a publisher's email reply to an ad placement pitch.
Respond with ONLY a JSON object, no markdown, no explanation:
{
  "intent": "approved" | "rejected" | "counter",
  "counter_amount": <integer or null>,
  "summary": "<one sentence>"
}
"""


async def classify_reply(email_body: str) -> dict:
    msg = await claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=200,
        system=INTENT_SYSTEM_PROMPT,
        messages=[{"role": "user", "content": email_body}],
    )
    text = msg.content[0].text.strip()
    return json.loads(text)


def _fetch_outreach_by_resend(sb: Client, resend_id: str) -> dict | None:
    r = (
        sb.table("outreach_logs")
        .select("*")
        .eq("resend_id", resend_id)
        .limit(1)
        .execute()
    )
    if not r.data:
        return None
    return r.data[0]


def _update_outreach_reply(
    sb: Client,
    outreach_id: str,
    intent: str,
    body: str,
    counter_amount,
) -> None:
    sb.table("outreach_logs").update(
        {
            "status": intent,
            "reply_raw": body[:5000],
            "reply_intent": intent,
            "counter_amount": counter_amount,
            "replied_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", outreach_id).execute()


def _insert_reply_event(sb: Client, campaign_id: str, message: str, intent: str, from_email: str) -> None:
    sb.table("agent_events").insert(
        {
            "campaign_id": campaign_id,
            "event_type": "reply",
            "message": message,
            "metadata": {"intent": intent, "from": from_email},
        }
    ).execute()


@router.post("/reply")
async def handle_reply(request: Request, sb: Client = Depends(get_supabase)):
    """
    Resend inbound webhook. Configure your Resend inbound address to POST here.
    Resend sends multipart/form-data with: from, to, subject, text, html, headers.
    """
    form = await request.form()
    from_email = form.get("from", "")
    subject = form.get("subject", "")
    body = form.get("text") or form.get("html") or ""
    in_reply_to = form.get("inReplyTo") or form.get("in-reply-to") or ""

    if not body:
        raise HTTPException(status_code=400, detail="Empty email body")

    outreach_row = None
    if in_reply_to:
        rid = in_reply_to.strip("<>")
        outreach_row = await asyncio.to_thread(_fetch_outreach_by_resend, sb, rid)

    try:
        classification = await classify_reply(body[:2000])
    except Exception as e:
        classification = {"intent": "unknown", "counter_amount": None, "summary": str(e)}

    intent = classification.get("intent", "unknown")

    if outreach_row:
        await asyncio.to_thread(
            _update_outreach_reply,
            sb,
            str(outreach_row["id"]),
            intent,
            body,
            classification.get("counter_amount"),
        )

        campaign_id = outreach_row["campaign_id"]
        await asyncio.to_thread(
            _insert_reply_event,
            sb,
            str(campaign_id),
            f"Reply from {from_email}: {classification.get('summary', '')}",
            intent,
            str(from_email),
        )

        # TODO: based on intent, trigger next step:
        # approved  → creative_pipeline.trigger(outreach_row["id"])
        # counter   → outreach_agent.counter(outreach_row["id"], classification["counter_amount"])
        # rejected  → outreach_agent.next_publisher(campaign_id)

    return {"received": True, "intent": intent}
