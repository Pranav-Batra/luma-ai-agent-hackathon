"""
Outreach Agent
Flow: campaign + publisher → Claude writes pitch email → Resend sends it
      → log to outreach_logs → log agent_event for dashboard stream
"""

import os
import json
import asyncio
import httpx
import anthropic
from uuid import UUID
from uuid import uuid4
import re
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv

load_dotenv()


from supabase import Client

# claude = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")
OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"

GMAIL_USER = os.environ.get("GMAIL_USER")  # your_email@gmail.com
GMAIL_APP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")  # app password

PITCH_SYSTEM_PROMPT = """
You are a direct media buyer writing cold outreach emails to website ad-ops managers.
Write a short, direct email proposing a paid banner ad placement.

Rules:
- 4 sentences maximum
- No fluff, no "I hope this email finds you well"
- Mention something specific about their site (use the trending headline provided)
- Propose a concrete dollar amount
- Give a 48-hour deadline to create urgency
- Sign off as "Alex, Media Buying Agent"

Respond with ONLY a JSON object, no markdown:
{
  "subject": "<email subject line>",
  "body": "<full email body, plain text>"
}
"""


def extract_json(text: str) -> dict:
    if not text:
        raise ValueError("Empty response from model")

    match = re.search(r"\{.*\}", text, re.DOTALL)
    if not match:
        raise ValueError(f"No JSON found in response: {text}")

    return json.loads(match.group())

async def generate_pitch(
    publisher_url: str,
    trending_headline: str,
    client_name: str,
    client_desc: str,
    audience: str,
    offer_amount: int,
) -> dict:
    """Call Claude to write a personalized pitch email."""
    user_prompt = f"""
Publisher site: {publisher_url}
Their trending article: "{trending_headline}"
Advertiser: {client_name}
Product: {client_desc}
Target audience: {audience}
Offer amount: ${offer_amount} for a 300x250 banner slot (30 days)
"""
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
                    {"role": "system", "content": PITCH_SYSTEM_PROMPT},
                    {"role": "user", "content": user_prompt},
                ],
                "max_tokens": 500,
            },
        )

    data = res.json()

    print("OPENROUTER RAW RESPONSE:", data)


    # Debug if needed
    if "error" in data:
        raise RuntimeError(f"OpenRouter error: {data['error']}")

    text = data["choices"][0]["message"]["content"].strip()
    print("MODEL TEXT:", text)
    return extract_json(text)


def _fetch_campaign(sb: Client, campaign_id: str) -> dict:
    r = sb.table("campaigns").select("*").eq("id", campaign_id).execute()
    if not r.data:
        raise ValueError(f"Campaign {campaign_id} not found")
    return r.data[0]


def _fetch_publisher(sb: Client, publisher_id: str) -> dict:
    r = sb.table("publishers").select("*").eq("id", publisher_id).execute()
    if not r.data:
        raise ValueError(f"Publisher {publisher_id} not found")
    return r.data[0]


def _log_outreach(sb: Client, campaign_id: str, publisher_id: str,
                  offer_amount: int, subject: str, body: str, resend_id: str) -> dict:
    r = sb.table("outreach_logs").insert({
        "campaign_id": campaign_id,
        "publisher_id": publisher_id,
        "offer_amount": offer_amount,
        "email_subject": subject,
        "email_body": body,
        "resend_id": resend_id,
        "status": "sent",
    }).execute()
    if not r.data:
        raise RuntimeError("outreach_logs insert returned no data")
    return r.data[0]


def _log_agent_event(sb: Client, campaign_id: str, message: str, metadata: dict) -> None:
    sb.table("agent_events").insert({
        "campaign_id": campaign_id,
        "event_type": "outreach",
        "message": message,
        "metadata": metadata,
    }).execute()


def _get_top_publishers(sb: Client, campaign_id: str, max_publishers: int) -> list:
    """Get top scored publishers not yet contacted for this campaign."""
    contacted = sb.table("outreach_logs") \
        .select("publisher_id") \
        .eq("campaign_id", campaign_id) \
        .execute()
    contacted_ids = [r["publisher_id"] for r in (contacted.data or [])]

    query = sb.table("publishers") \
        .select("*") \
        .not_.is_("contact_email", "null") \
        .order("score", desc=True) \
        .limit(max_publishers + len(contacted_ids))

    r = query.execute()
    publishers = r.data or []

    publishers = [p for p in publishers if p["id"] not in contacted_ids]
    return publishers[:max_publishers]


def _update_campaign_status(sb: Client, campaign_id: str, status: str) -> None:
    sb.table("campaigns").update({"status": status}).eq("id", campaign_id).execute()

def send_email_smtp(subject: str, body: str, to_email: str) -> str:
    msg = EmailMessage()
    msg["Subject"] = subject
    msg["From"] = GMAIL_USER
    msg["To"] = to_email
    msg.set_content(body)

    with smtplib.SMTP_SSL("smtp.gmail.com", 465) as smtp:
        smtp.login(GMAIL_USER, GMAIL_APP_PASSWORD)
        smtp.send_message(msg)

    return "smtp-" + str(uuid4())  # fake ID for logging
    
async def send_outreach(
    sb: Client,
    campaign_id: str,
    publisher_id: str,
    offer_amount: int,
) -> dict:
    campaign = await asyncio.to_thread(_fetch_campaign, sb, campaign_id)
    publisher = await asyncio.to_thread(_fetch_publisher, sb, publisher_id)

    if not publisher.get("contact_email"):
        raise ValueError(f"Publisher {publisher['url']} has no contact email")

    headlines = publisher.get("trending_headlines") or []
    headline = headlines[0] if headlines else "your recent content"

    pitch = await generate_pitch(
        publisher_url=publisher["url"],
        trending_headline=headline,
        client_name=campaign["client_name"],
        client_desc=campaign["product_desc"],
        audience=campaign["audience"],
        offer_amount=offer_amount,
    )

    resend_id = send_email_smtp(
        subject=pitch['subject'], 
        body=pitch['body'],
        to_email="pokihi8550@lealking.com"
    )

    # response = resend.Emails.send({
    #     "from": FROM_EMAIL,
    #     "to": "pokihi8550@lealking.com", ##temporary email that acts on behalf of all publishers
    #     # "to": publisher["contact_email"],
    #     "subject": pitch["subject"],
    #     "text": pitch["body"],
    # })
    # resend_id = response.get("id")



    outreach = await asyncio.to_thread(
        _log_outreach, sb, campaign_id, publisher_id,
        offer_amount, pitch["subject"], pitch["body"], resend_id
    )

    await asyncio.to_thread(
        _log_agent_event, sb, campaign_id,
        f"Sent pitch to {publisher['contact_email']} ({publisher['url']}) — offer ${offer_amount}",
        {
            "publisher_id": publisher_id,
            "publisher_url": publisher["url"],
            "contact_email": publisher["contact_email"],
            "offer_amount": offer_amount,
            "resend_id": resend_id,
            "subject": pitch["subject"],
        },
    )

    return {
        "outreach_id": outreach["id"],
        "resend_id": resend_id,
        "to": publisher["contact_email"],
        "subject": pitch["subject"],
        "body": pitch["body"],
        "offer_amount": offer_amount,
    }


async def run_outreach_for_campaign(
    sb: Client,
    campaign_id: str,
    max_publishers: int = 3,
) -> list:
    campaign = await asyncio.to_thread(_fetch_campaign, sb, campaign_id)
    publishers = await asyncio.to_thread(_get_top_publishers, sb, campaign_id, max_publishers)

    if not publishers:
        await asyncio.to_thread(
            _log_agent_event, sb, campaign_id,
            "No eligible publishers found — run recon on seed URLs first", {}
        )
        return []

    offer_per_publisher = int((campaign["budget"] * 0.4) / len(publishers))

    results = []
    for pub in publishers:
        try:
            result = await send_outreach(
                sb=sb,
                campaign_id=campaign_id,
                publisher_id=pub["id"],
                offer_amount=offer_per_publisher,
            )
            results.append(result)
        except Exception as e:
            await asyncio.to_thread(
                _log_agent_event, sb, campaign_id,
                f"Failed to contact {pub['url']}: {str(e)}",
                {"error": str(e), "publisher_url": pub["url"]},
            )

    return results