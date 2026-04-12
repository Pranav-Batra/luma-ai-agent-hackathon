# """
# SECOND PART OF OUTREACH -> IF PUBLISHER(I.E NYT) RESPONDS WITH APPROVAL TO PITCH REQUEST, THIS GETS TRIGGERED TO CREATE THE AD
# Creative pipeline: Claude writes ad copy → persist ad_creatives → optional delivery email with ad tag URLs.
# """

# from __future__ import annotations

# import asyncio
# import json
# import os
# import uuid
# from datetime import datetime, timezone
# from helper import extract_json

# # import anthropic
# import httpx
# # import resend
# from supabase import Client

# # claude = anthropic.AsyncAnthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))
# # resend.api_key = os.environ.get("RESEND_API_KEY")
# FROM_EMAIL = os.environ.get("RESEND_FROM_EMAIL", "agent@yourdomain.com")
# OPENROUTER_URL="https://openrouter.ai/api/v1/chat/completions"
# OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# PUBLIC_API_BASE = os.environ.get("PUBLIC_API_BASE", "http://127.0.0.1:8000").rstrip("/")
# DEFAULT_AD_DESTINATION = os.environ.get("DEFAULT_AD_DESTINATION", "https://example.com")
# PLACEHOLDER_IMAGE = os.environ.get(
#     "AD_PLACEHOLDER_IMAGE_URL",
#     "https://placehold.co/300x250/1a1a2e/eeeeee?text=300x250+Ad",
# )

# CREATIVE_SYSTEM = """
# You write display ad copy for a 300x250 banner placement.
# Return ONLY a JSON object, no markdown:
# {
#   "headline": "<max ~40 chars>",
#   "subheadline": "<max ~90 chars, optional context>",
#   "cta": "<max ~24 chars, button text>"
# }
# Tie the message to the publisher's audience and the trending topic when relevant.
# """


# async def generate_creative_copy(
#     client_name: str,
#     product_desc: str,
#     audience: str,
#     publisher_url: str,
#     trending_headline: str,
#     offer_amount: int,
# ) -> dict:
#     user = f"""
# Advertiser: {client_name}
# Product: {product_desc}
# Audience: {audience}
# Publisher site: {publisher_url}
# Trending on site: "{trending_headline}"
# Deal value: ${offer_amount}
# """
#     async with httpx.AsyncClient() as client:
#         res = await client.post(
#             OPENROUTER_URL,
#             headers={
#                 "Authorization": f"Bearer {OPENROUTER_API_KEY}",
#                 "Content-Type": "application/json",
#             },
#             json={
#                 "model": "anthropic/claude-3.5-haiku",  # or newer if available
#                 "messages": [
#                     {"role": "system", "content": CREATIVE_SYSTEM},
#                     {"role": "user", "content": user},
#                 ],
#                 "max_tokens": 500,
#             },
#         )

#     data = res.json()

#     print("OPENROUTER RAW RESPONSE:", data)


#     # Debug if needed
#     if "error" in data:
#         raise RuntimeError(f"OpenRouter error: {data['error']}")

#     text = data["choices"][0]["message"]["content"].strip()
#     print("MODEL TEXT:", text)
#     return extract_json(text)
#     msg = await claude.messages.create(
#         model="claude-sonnet-4-20250514",
#         max_tokens=400,
#         system=CREATIVE_SYSTEM,
#         messages=[{"role": "user", "content": user}],
#     )
#     text = msg.content[0].text.strip()
#     return json.loads(text)


# def insert_ad_creative(
#     sb: Client,
#     campaign_id: str,
#     outreach_id: str,
#     headline: str,
#     subheadline: str | None,
#     cta: str | None,
#     image_url: str | None,
# ) -> dict:
#     click_track_id = str(uuid.uuid4())
#     banner_url = f"{PUBLIC_API_BASE}/api/ads/{click_track_id}/click"
#     row = {
#         "campaign_id": campaign_id,
#         "outreach_id": outreach_id,
#         "headline": headline,
#         "subheadline": subheadline,
#         "cta": cta,
#         "image_url": image_url or PLACEHOLDER_IMAGE,
#         "banner_url": banner_url,
#         "click_track_id": click_track_id,
#     }
#     r = sb.table("ad_creatives").insert(row).execute()
#     if not r.data:
#         raise RuntimeError("ad_creatives insert returned no data")
#     return r.data[0]


# def _log_event(sb: Client, campaign_id: str, message: str, metadata: dict) -> None:
#     sb.table("agent_events").insert(
#         {
#             "campaign_id": campaign_id,
#             "event_type": "creative",
#             "message": message,
#             "metadata": metadata,
#         }
#     ).execute()


# def _fetch_campaign(sb: Client, campaign_id: str) -> dict:
#     r = sb.table("campaigns").select("*").eq("id", campaign_id).execute()
#     if not r.data:
#         raise ValueError("Campaign not found")
#     return r.data[0]


# def _fetch_publisher(sb: Client, publisher_id: str) -> dict:
#     r = sb.table("publishers").select("*").eq("id", publisher_id).execute()
#     if not r.data:
#         raise ValueError("Publisher not found")
#     return r.data[0]


# def _bump_campaign_spend(sb: Client, campaign_id: str, amount: int) -> None:
#     c = _fetch_campaign(sb, campaign_id)
#     new_spend = int(c.get("spend") or 0) + int(amount)
#     sb.table("campaigns").update(
#         {
#             "spend": new_spend,
#             "updated_at": datetime.now(timezone.utc).isoformat(),
#         }
#     ).eq("id", campaign_id).execute()


# async def run_approved_pipeline(sb: Client, outreach_row: dict) -> dict | None:
#     """
#     Generate creative, persist ad_creatives, log event, email publisher with placement instructions.
#     """
#     campaign_id = str(outreach_row["campaign_id"])
#     publisher_id = str(outreach_row["publisher_id"])
#     outreach_id = str(outreach_row["id"])
#     offer_amount = int(outreach_row["offer_amount"])

#     campaign = await asyncio.to_thread(_fetch_campaign, sb, campaign_id)
#     publisher = await asyncio.to_thread(_fetch_publisher, sb, publisher_id)

#     headlines = publisher.get("trending_headlines") or []
#     trending = headlines[0] if headlines else "your readers"

#     copy = await generate_creative_copy(
#         client_name=campaign["client_name"],
#         product_desc=campaign["product_desc"],
#         audience=campaign["audience"],
#         publisher_url=publisher["url"],
#         trending_headline=trending,
#         offer_amount=offer_amount,
#     )

#     creative = await asyncio.to_thread(
#         insert_ad_creative,
#         sb,
#         campaign_id,
#         outreach_id,
#         copy["headline"],
#         copy.get("subheadline"),
#         copy.get("cta"),
#         PLACEHOLDER_IMAGE,
#     )

#     await asyncio.to_thread(_bump_campaign_spend, sb, campaign_id, offer_amount)

#     click_url = f"{PUBLIC_API_BASE}/api/ads/{creative['click_track_id']}/click"
#     img = creative.get("image_url") or PLACEHOLDER_IMAGE

#     await asyncio.to_thread(
#         _log_event,
#         sb,
#         campaign_id,
#         f"Creative ready for {publisher['url']}: \"{copy['headline']}\"",
#         {
#             "ad_creative_id": creative["id"],
#             "click_track_id": creative["click_track_id"],
#             "headline": copy["headline"],
#         },
#     )

#     to = publisher.get("contact_email")
#     if to and FROM_EMAIL:
#     # if to and resend.api_key and FROM_EMAIL:
#         delivery = f"""Thanks for approving the placement.

# Here is your 300x250 creative:
# Headline: {copy['headline']}
# {f"Subheadline: {copy['subheadline']}" if copy.get("subheadline") else ""}
# {f"CTA: {copy['cta']}" if copy.get("cta") else ""}

# Image (placeholder): {img}
# Click-through URL (tracks clicks): {click_url}

# Paste this HTML where the slot should run:
# <a href="{click_url}"><img src="{img}" width="300" height="250" alt="{copy['headline']}" /></a>

# — Alex, Media Buying Agent
# """
#         try:
#             resend.Emails.send(
#                 {
#                     "from": FROM_EMAIL,
#                     "to": to,
#                     "subject": f"Re: {outreach_row.get('email_subject') or 'Ad placement'} — creative + tag",
#                     "text": delivery,
#                 }
#             )
#         except Exception as exc:
#             await asyncio.to_thread(
#                 _log_event,
#                 sb,
#                 campaign_id,
#                 f"Creative saved but delivery email failed: {exc}",
#                 {"ad_creative_id": creative["id"], "error": str(exc)},
#             )

#     return {
#         "ad_creative_id": creative["id"],
#         "click_track_id": creative["click_track_id"],
#         "headline": copy["headline"],
#     }
"""
SECOND PART OF OUTREACH -> IF PUBLISHER(I.E NYT) RESPONDS WITH APPROVAL TO PITCH REQUEST, THIS GETS TRIGGERED TO CREATE THE AD
Creative pipeline: Claude writes ad copy → persist ad_creatives → send delivery email via SMTP.
"""

from __future__ import annotations

import asyncio
import json
import os
import smtplib
import uuid
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from datetime import datetime, timezone
from urllib.parse import quote
from app.agents.helper import extract_json

import httpx
from supabase import Client

OPENROUTER_URL = "https://openrouter.ai/api/v1/chat/completions"
OPENROUTER_API_KEY = os.environ.get("OPENROUTER_API_KEY")

# SMTP config — same account you use for outbound pitches
SMTP_HOST = os.environ.get("SMTP_HOST", "smtp.gmail.com")
SMTP_PORT = int(os.environ.get("SMTP_PORT", 587))
SMTP_USER = os.environ.get("GMAIL_USER")
SMTP_PASSWORD = os.environ.get("GMAIL_APP_PASSWORD")
FROM_EMAIL = os.environ.get("GMAIL_USER")

PUBLIC_API_BASE = os.environ.get("PUBLIC_API_BASE", "http://127.0.0.1:8000").rstrip("/")
PLACEHOLDER_IMAGE = os.environ.get(
    "AD_PLACEHOLDER_IMAGE_URL",
    "https://placehold.co/300x250/1a1a2e/eeeeee?text=300x250+Ad",
)

# Free display-ad images: Pollinations public image URL (no API key).
# The URL embeds the prompt; the server returns a JPEG when the image is requested.
# See https://pollinations.ai — we use the classic image.pollinations.ai/prompt/... endpoint.
POLLINATIONS_IMAGE_BASE = os.environ.get(
    "POLLINATIONS_IMAGE_BASE",
    "https://image.pollinations.ai/prompt",
)
AD_USE_POLLINATIONS_IMAGE = os.environ.get("AD_USE_POLLINATIONS_IMAGE", "true").lower() in (
    "1",
    "true",
    "yes",
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


# ── LLM ──────────────────────────────────────────────────────────────────────

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
    async with httpx.AsyncClient() as client:
        res = await client.post(
            OPENROUTER_URL,
            headers={
                "Authorization": f"Bearer {OPENROUTER_API_KEY}",
                "Content-Type": "application/json",
            },
            json={
                "model": "anthropic/claude-3.5-haiku",
                "messages": [
                    {"role": "system", "content": CREATIVE_SYSTEM},
                    {"role": "user", "content": user},
                ],
                "max_tokens": 500,
            },
        )

    data = res.json()
    print("OPENROUTER RAW RESPONSE:", data)

    if "error" in data:
        raise RuntimeError(f"OpenRouter error: {data['error']}")

    text = data["choices"][0]["message"]["content"].strip()
    print("MODEL TEXT:", text)
    return extract_json(text)


# ── Banner image (Pollinations — free, no API key) ───────────────────────────

def _build_visual_prompt_for_image(
    client_name: str,
    product_desc: str,
    headline: str,
    subheadline: str | None,
    cta: str | None,
    publisher_url: str,
    trending: str,
) -> str:
    """Describe the *visual* for the banner; avoid tiny text (copy lives in the email)."""
    sub = f" {subheadline}" if subheadline else ""
    cta_p = f" Call to action mood: {cta}." if cta else ""
    return (
        f"Professional 300x250 style web display advertisement, wide banner composition, "
        f"brand {client_name}, product {product_desc}, theme {headline}.{sub}{cta_p} "
        f"Publisher context {publisher_url}, trending {trending}. "
        f"Bold colors, high contrast, modern commercial layout, no small illegible text, "
        f"no watermarks, sharp focus."
    )[:1500]


def build_pollinations_ad_image_url(
    *,
    client_name: str,
    product_desc: str,
    headline: str,
    subheadline: str | None,
    cta: str | None,
    publisher_url: str,
    trending_headline: str,
) -> str | None:
    """
    Returns a Pollinations image URL, or None if disabled / empty prompt.
    No API key: the service generates from the URL path when the image is fetched.
    """
    if not AD_USE_POLLINATIONS_IMAGE:
        return None
    prompt = _build_visual_prompt_for_image(
        client_name,
        product_desc,
        headline,
        subheadline,
        cta,
        publisher_url,
        trending_headline,
    ).strip()
    if not prompt:
        return None
    # Path segment must be percent-encoded; safe='' so spaces become %20.
    encoded = quote(prompt, safe="")
    return f"{POLLINATIONS_IMAGE_BASE.rstrip('/')}/{encoded}"


def resolve_ad_image_url(
    *,
    client_name: str,
    product_desc: str,
    headline: str,
    subheadline: str | None,
    cta: str | None,
    publisher_url: str,
    trending_headline: str,
) -> tuple[str, bool]:
    """
    (image_url, used_pollinations). Falls back to PLACEHOLDER_IMAGE if Pollinations is off
    or URL could not be built.
    """
    url = build_pollinations_ad_image_url(
        client_name=client_name,
        product_desc=product_desc,
        headline=headline,
        subheadline=subheadline,
        cta=cta,
        publisher_url=publisher_url,
        trending_headline=trending_headline,
    )
    if url:
        return url, True
    return PLACEHOLDER_IMAGE, False


# ── Email ─────────────────────────────────────────────────────────────────────

def _send_smtp(to: str, subject: str, body: str) -> None:
    """Send a plain-text email via Gmail SMTP."""
    msg = MIMEMultipart()
    msg["From"] = FROM_EMAIL
    msg["To"] = to
    msg["Subject"] = subject
    msg.attach(MIMEText(body, "plain"))

    with smtplib.SMTP(SMTP_HOST, SMTP_PORT) as server:
        server.ehlo()
        server.starttls()
        server.login(SMTP_USER, SMTP_PASSWORD)
        server.sendmail(FROM_EMAIL, to, msg.as_string())


# ── DB helpers ────────────────────────────────────────────────────────────────

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
    sb.table("agent_events").insert({
        "campaign_id": campaign_id,
        "event_type": "creative",
        "message": message,
        "metadata": metadata,
    }).execute()


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
    sb.table("campaigns").update({
        "spend": new_spend,
        "updated_at": datetime.now(timezone.utc).isoformat(),
    }).eq("id", campaign_id).execute()


# ── Main pipeline ─────────────────────────────────────────────────────────────

async def run_approved_pipeline(sb: Client, outreach_row: dict) -> dict | None:
    """
    Generate creative, persist ad_creatives, log event,
    email publisher with placement instructions via SMTP.
    """
    campaign_id = str(outreach_row["campaign_id"])
    publisher_id = str(outreach_row["publisher_id"])
    outreach_id = str(outreach_row["id"])
    offer_amount = int(outreach_row["offer_amount"])

    campaign = await asyncio.to_thread(_fetch_campaign, sb, campaign_id)
    publisher = await asyncio.to_thread(_fetch_publisher, sb, publisher_id)

    headlines = publisher.get("trending_headlines") or []
    trending = headlines[0] if headlines else "your readers"

    # Generate copy with LLM
    copy = await generate_creative_copy(
        client_name=campaign["client_name"],
        product_desc=campaign["product_desc"],
        audience=campaign["audience"],
        publisher_url=publisher["url"],
        trending_headline=trending,
        offer_amount=offer_amount,
    )

    image_url, image_from_pollinations = resolve_ad_image_url(
        client_name=campaign["client_name"],
        product_desc=campaign["product_desc"],
        headline=copy["headline"],
        subheadline=copy.get("subheadline"),
        cta=copy.get("cta"),
        publisher_url=publisher["url"],
        trending_headline=trending,
    )

    # Persist creative to DB
    creative = await asyncio.to_thread(
        insert_ad_creative,
        sb,
        campaign_id,
        outreach_id,
        copy["headline"],
        copy.get("subheadline"),
        copy.get("cta"),
        image_url,
    )

    # Update campaign spend
    await asyncio.to_thread(_bump_campaign_spend, sb, campaign_id, offer_amount)

    click_url = f"{PUBLIC_API_BASE}/api/ads/{creative['click_track_id']}/click"
    img = creative.get("image_url") or PLACEHOLDER_IMAGE
    image_line = (
        f"Image (AI-generated, Pollinations — free, no key): {img}"
        if image_from_pollinations
        else f"Image (placeholder): {img}"
    )

    # Log agent event
    await asyncio.to_thread(
        _log_event,
        sb,
        campaign_id,
        f"Creative ready for {publisher['url']}: \"{copy['headline']}\"",
        {
            "ad_creative_id": creative["id"],
            "click_track_id": creative["click_track_id"],
            "headline": copy["headline"],
            "image_provider": "pollinations" if image_from_pollinations else "placeholder",
        },
    )

    # Send delivery email to publisher via SMTP
    to = publisher.get("contact_email")
    if to and FROM_EMAIL and SMTP_PASSWORD:
        subheadline_line = f"Subheadline: {copy['subheadline']}" if copy.get("subheadline") else ""
        cta_line = f"CTA: {copy['cta']}" if copy.get("cta") else ""

        delivery = f"""Thanks for approving the placement.

Here is your 300x250 creative:
Headline: {copy['headline']}
{subheadline_line}
{cta_line}

{image_line}
Click-through URL (tracks clicks): {click_url}

Paste this HTML where the slot should run:
<a href="{click_url}"><img src="{img}" width="300" height="250" alt="{copy['headline']}" /></a>

— Alex, Media Buying Agent
"""
        subject = f"Re: {outreach_row.get('email_subject') or 'Ad placement'} — creative + tag"
        print(f'DELIVERY: {delivery}')
        try:
            await asyncio.to_thread(_send_smtp, to, subject, delivery)
            await asyncio.to_thread(
                _log_event,
                sb,
                campaign_id,
                f"Delivery email sent to {to}",
                {"ad_creative_id": creative["id"], "to": to},
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