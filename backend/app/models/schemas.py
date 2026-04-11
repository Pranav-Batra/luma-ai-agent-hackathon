from pydantic import BaseModel, HttpUrl
from typing import Optional
from uuid import UUID
from datetime import datetime


# ── Campaigns ────────────────────────────────────────────────────────────────

class CampaignCreate(BaseModel):
    client_name: str
    product_desc: str
    budget: int                     # dollars
    audience: str
    seed_urls: list[str] = []


class CampaignOut(BaseModel):
    id: UUID
    client_name: str
    product_desc: str
    budget: int
    audience: str
    seed_urls: list[str]
    status: str
    spend: int
    impressions: int
    created_at: datetime
    updated_at: datetime


# ── Publishers ────────────────────────────────────────────────────────────────

class PublisherOut(BaseModel):
    id: UUID
    url: str
    contact_email: Optional[str]
    ad_networks: list[str]
    estimated_traffic: Optional[str]
    score: int
    has_adsense: bool
    has_premium_dsp: bool
    trending_headlines: list[str]
    created_at: datetime


# ── Recon ─────────────────────────────────────────────────────────────────────

class ReconRequest(BaseModel):
    url: str
    campaign_id: Optional[UUID] = None


class ReconResult(BaseModel):
    url: str
    ad_networks: list[str]
    contact_email: Optional[str]
    estimated_traffic: str
    has_adsense: bool
    has_premium_dsp: bool
    trending_headlines: list[str]
    score: int


# ── Outreach ──────────────────────────────────────────────────────────────────

class OutreachRequest(BaseModel):
    campaign_id: UUID
    publisher_id: UUID
    offer_amount: int


class OutreachLogOut(BaseModel):
    id: UUID
    campaign_id: UUID
    publisher_id: UUID
    offer_amount: int
    email_subject: Optional[str]
    email_body: Optional[str]
    status: str
    reply_intent: Optional[str]
    created_at: datetime
    replied_at: Optional[datetime]


# ── Webhook ───────────────────────────────────────────────────────────────────

class ResendWebhookPayload(BaseModel):
    type: str                       # e.g. "email.delivered", "email.opened"
    data: dict


class ReplyWebhookPayload(BaseModel):
    from_email: str
    subject: str
    body_plain: str
    in_reply_to: Optional[str] = None  # Resend message ID of original


# ── Agent Events ──────────────────────────────────────────────────────────────

class AgentEventOut(BaseModel):
    id: UUID
    campaign_id: Optional[UUID]
    event_type: str
    message: str
    metadata: dict
    created_at: datetime