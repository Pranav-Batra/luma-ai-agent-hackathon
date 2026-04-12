"""
Creative pipeline: Claude writes ad copy → persist ad_creatives → optional delivery email with ad tag URLs.
"""

from __future__ import annotations

import asyncio
import json
import os
import uuid
from datetime import datetime, timezone

import anthropic
import resend
from supabase import Client

claude = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
resend.api_key = os.environ.get("RESEND_API_KEY")
FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "agent@yourdomain.com")

PUBLIC_API_BASE = os.environ.get("PUBLIC_API_BASE", "http://127.0.0.1:8000").rstrip("/")
DEFAULT_AD_DESTINATION = os.environ.get("DEFAULT_AD_DESTINATION", "https://example.com")
PLACEHOLDER_IMAGE = os.environ.get(
    "AD_PLACEHOLDER_IMAGE_URL",
    "https://placehold.co/300x250/1a1a2e/eeeeee?text=300x250+Ad",
)

CREATIVE_SYSTEM = """
You write display ad copy for a 300x250 banner placement.
Return ONLY a JSON object, no markdown:
{
  "headline": "<max ~40 chars>",
  "subheadline": "<max ~90 chars, optional context>",
  "cta": "<max ~24 chars, button text>"
}
Tie the message to the publisher's audience and the trending topic when relevant.
"""


async def generate_creative_copy(
    client_name: str,
    product_desc: str,
    audience: str,
    publisher_url: str,
    trending_headline: str,
    offer_amount: int,
) -> dict:
    user = f"""
Advertiser: {client_name}
Product: {product_desc}
Audience: {audience}
Publisher site: {publisher_url}
Trending on site: "{trending_headline}"
Deal value: ${offer_amount}
"""
    msg = await claude.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=400,
        system=CREATIVE_SYSTEM,
        messages=[{"role": "user", "content": user}],
    )
    text = msg.content[0].text.strip()
    return json.loads(text)


def insert_ad_creative(
    sb: Client,
    campaign_id: str,
    outreach_id: str,
    headline: str,
    subheadline: str | None,
    cta: str | None,
    image_url: str | None,
) -> dict:
    click_track_id = str(uuid.uuid4())
    banner_url = f"{PUBLIC_API_BASE}/api/ads/{click_track_id}/click"
    row = {
        "campaign_id": campaign_id,
        "outreach_id": outreach_id,
        "headline": headline,
        "subheadline": subheadline,
        "cta": cta,
        "image_url": image_url or PLACEHOLDER_IMAGE,
        "banner_url": banner_url,
        "click_track_id": click_track_id,
    }
    r = sb.table("ad_creatives").insert(row).execute()
    if not r.data:
        raise RuntimeError("ad_creatives insert returned no data")
    return r.data[0]


def _log_event(sb: Client, campaign_id: str, message: str, metadata: dict) -> None:
    sb.table("agent_events").insert(
        {
            "campaign_id": campaign_id,
            "event_type": "creative",
            "message": message,
            "metadata": metadata,
        }
    ).execute()


def _fetch_campaign(sb: Client, campaign_id: str) -> dict:
    r = sb.table("campaigns").select("*").eq("id", campaign_id).execute()
    if not r.data:
        raise ValueError("Campaign not found")
    return r.data[0]


def _fetch_publisher(sb: Client, publisher_id: str) -> dict:
    r = sb.table("publishers").select("*").eq("id", publisher_id).execute()
    if not r.data:
        raise ValueError("Publisher not found")
    return r.data[0]


def _bump_campaign_spend(sb: Client, campaign_id: str, amount: int) -> None:
    c = _fetch_campaign(sb, campaign_id)
    new_spend = int(c.get("spend") or 0) + int(amount)
    sb.table("campaigns").update(
        {
            "spend": new_spend,
            "updated_at": datetime.now(timezone.utc).isoformat(),
        }
    ).eq("id", campaign_id).execute()


async def run_approved_pipeline(sb: Client, outreach_row: dict) -> dict | None:
    """
    Generate creative, persist ad_creatives, log event, email publisher with placement instructions.
    """
    campaign_id = str(outreach_row["campaign_id"])
    publisher_id = str(outreach_row["publisher_id"])
    outreach_id = str(outreach_row["id"])
    offer_amount = int(outreach_row["offer_amount"])

    campaign = await asyncio.to_thread(_fetch_campaign, sb, campaign_id)
    publisher = await asyncio.to_thread(_fetch_publisher, sb, publisher_id)

    headlines = publisher.get("trending_headlines") or []
    trending = headlines[0] if headlines else "your readers"

    copy = await generate_creative_copy(
        client_name=campaign["client_name"],
        product_desc=campaign["product_desc"],
        audience=campaign["audience"],
        publisher_url=publisher["url"],
        trending_headline=trending,
        offer_amount=offer_amount,
    )

    creative = await asyncio.to_thread(
        insert_ad_creative,
        sb,
        campaign_id,
        outreach_id,
        copy["headline"],
        copy.get("subheadline"),
        copy.get("cta"),
        PLACEHOLDER_IMAGE,
    )

    await asyncio.to_thread(_bump_campaign_spend, sb, campaign_id, offer_amount)

    click_url = f"{PUBLIC_API_BASE}/api/ads/{creative['click_track_id']}/click"
    img = creative.get("image_url") or PLACEHOLDER_IMAGE

    await asyncio.to_thread(
        _log_event,
        sb,
        campaign_id,
        f"Creative ready for {publisher['url']}: \"{copy['headline']}\"",
        {
            "ad_creative_id": creative["id"],
            "click_track_id": creative["click_track_id"],
            "headline": copy["headline"],
        },
    )

    to = publisher.get("contact_email")
    if to and resend.api_key and FROM_EMAIL:
        delivery = f"""Thanks for approving the placement.

Here is your 300x250 creative:
Headline: {copy['headline']}
{f"Subheadline: {copy['subheadline']}" if copy.get("subheadline") else ""}
{f"CTA: {copy['cta']}" if copy.get("cta") else ""}

Image (placeholder): {img}
Click-through URL (tracks clicks): {click_url}

Paste this HTML where the slot should run:
<a href="{click_url}"><img src="{img}" width="300" height="250" alt="{copy['headline']}" /></a>

— Alex, Media Buying Agent
"""
        try:
            resend.Emails.send(
                {
                    "from": FROM_EMAIL,
                    "to": to,
                    "subject": f"Re: {outreach_row.get('email_subject') or 'Ad placement'} — creative + tag",
                    "text": delivery,
                }
            )
        except Exception as exc:
            await asyncio.to_thread(
                _log_event,
                sb,
                campaign_id,
                f"Creative saved but delivery email failed: {exc}",
                {"ad_creative_id": creative["id"], "error": str(exc)},
            )

    return {
        "ad_creative_id": creative["id"],
        "click_track_id": creative["click_track_id"],
        "headline": copy["headline"],
    }
