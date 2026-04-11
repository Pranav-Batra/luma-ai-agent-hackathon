"""
Webhook handler for inbound publisher replies via Resend.
Flow: email arrives → Resend POSTs here → Claude classifies intent
      → approved: trigger creative pipeline
      → counter: Claude generates counter-counter and sends it
      → rejected: log and move to next publisher
"""
from fastapi import APIRouter, Depends, Request, HTTPException
import asyncpg
import anthropic
import os

from app.core.database import get_db

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
    import json
    text = msg.content[0].text.strip()
    return json.loads(text)


@router.post("/reply")
async def handle_reply(request: Request, db: asyncpg.Connection = Depends(get_db)):
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

    # Find the outreach log by Resend message ID
    outreach_row = None
    if in_reply_to:
        outreach_row = await db.fetchrow(
            "SELECT * FROM outreach_logs WHERE resend_id = $1", in_reply_to.strip("<>")
        )

    # Classify intent with Claude
    try:
        classification = await classify_reply(body[:2000])  # cap tokens
    except Exception as e:
        classification = {"intent": "unknown", "counter_amount": None, "summary": str(e)}

    intent = classification.get("intent", "unknown")

    # Update outreach log
    if outreach_row:
        await db.execute(
            """
            UPDATE outreach_logs
            SET status = $1, reply_raw = $2, reply_intent = $3,
                counter_amount = $4, replied_at = NOW()
            WHERE id = $5
            """,
            intent,
            body[:5000],
            intent,
            classification.get("counter_amount"),
            outreach_row["id"],
        )

        campaign_id = outreach_row["campaign_id"]

        # Log agent event
        await db.execute(
            """
            INSERT INTO agent_events (campaign_id, event_type, message, metadata)
            VALUES ($1, 'reply', $2, $3::jsonb)
            """,
            campaign_id,
            f"Reply from {from_email}: {classification.get('summary', '')}",
            f'{{"intent": "{intent}", "from": "{from_email}"}}',
        )

        # TODO: based on intent, trigger next step:
        # approved  → creative_pipeline.trigger(outreach_row["id"])
        # counter   → outreach_agent.counter(outreach_row["id"], classification["counter_amount"])
        # rejected  → outreach_agent.next_publisher(campaign_id)

    return {"received": True, "intent": intent}