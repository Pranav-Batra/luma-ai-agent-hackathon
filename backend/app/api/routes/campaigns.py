from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import json
import asyncio
from datetime import datetime, timezone
from uuid import UUID

from supabase import Client

from app.core.database import get_supabase
from app.models.schemas import CampaignCreate, CampaignOut

router = APIRouter()


def _insert_campaign(sb: Client, payload: CampaignCreate) -> dict:
    r = (
        sb.table("campaigns")
        .insert(
            {
                "client_name": payload.client_name,
                "product_desc": payload.product_desc,
                "budget": payload.budget,
                "audience": payload.audience,
                "seed_urls": payload.seed_urls,
            }
        )
        .execute()
    )
    if not r.data:
        raise HTTPException(status_code=500, detail="Failed to create campaign")
    return r.data[0]


@router.post("/", response_model=CampaignOut, status_code=201)
async def create_campaign(
    payload: CampaignCreate,
    sb: Client = Depends(get_supabase),
):
    return await asyncio.to_thread(_insert_campaign, sb, payload)


def _list_campaigns(sb: Client) -> list[dict]:
    r = sb.table("campaigns").select("*").order("created_at", desc=True).execute()
    return r.data or []


@router.get("/", response_model=list[CampaignOut])
async def list_campaigns(sb: Client = Depends(get_supabase)):
    return await asyncio.to_thread(_list_campaigns, sb)


def _get_campaign(sb: Client, campaign_id: UUID) -> dict | None:
    r = sb.table("campaigns").select("*").eq("id", str(campaign_id)).limit(1).execute()
    if not r.data:
        return None
    return r.data[0]


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: UUID, sb: Client = Depends(get_supabase)):
    row = await asyncio.to_thread(_get_campaign, sb, campaign_id)
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return row


def _set_campaign_running(sb: Client, campaign_id: UUID) -> dict | None:
    existing = (
        sb.table("campaigns").select("*").eq("id", str(campaign_id)).limit(1).execute()
    )
    if not existing.data:
        return None
    if existing.data[0]["status"] == "running":
        return {"error": "already_running", "row": existing.data[0]}
    r = (
        sb.table("campaigns")
        .update(
            {
                "status": "running",
                "updated_at": datetime.now(timezone.utc).isoformat(),
            }
        )
        .eq("id", str(campaign_id))
        .execute()
    )
    return {"error": None, "row": (r.data[0] if r.data else existing.data[0])}


@router.post("/{campaign_id}/run", status_code=202)
async def run_campaign(campaign_id: UUID, sb: Client = Depends(get_supabase)):
    """
    Kick off the full agent pipeline for a campaign.
    Updates status to 'running' and queues background work.
    In prod you'd hand this to a task queue (Celery, ARQ, etc).
    """
    out = await asyncio.to_thread(_set_campaign_running, sb, campaign_id)
    if not out:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if out["error"] == "already_running":
        raise HTTPException(status_code=409, detail="Campaign already running")
    # TODO: enqueue pipeline task → recon → score → outreach
    return {"message": "Campaign started", "campaign_id": str(campaign_id)}


def _event_ts(row: dict) -> str:
    t = row["created_at"]
    if isinstance(t, str):
        return t
    return t.isoformat()


def _fetch_events(sb: Client, campaign_id: UUID, last_id: str | None) -> list[dict]:
    q = (
        sb.table("agent_events")
        .select("*")
        .eq("campaign_id", str(campaign_id))
        .order("created_at", desc=False)
    )
    if last_id:
        q = q.gt("id", last_id)
    r = q.execute()
    return r.data or []


@router.get("/{campaign_id}/events")
async def campaign_events_stream(campaign_id: UUID, sb: Client = Depends(get_supabase)):
    """
    Server-Sent Events stream of agent_events for live dashboard feed.
    Frontend connects once; events push in real time.
    """

    async def event_generator():
        last_id = None
        while True:
            rows = await asyncio.to_thread(_fetch_events, sb, campaign_id, last_id)
            for row in rows:
                last_id = row["id"]
                md = row.get("metadata") or {}
                if isinstance(md, str):
                    try:
                        md = json.loads(md)
                    except json.JSONDecodeError:
                        md = {}
                data = json.dumps(
                    {
                        "id": str(row["id"]),
                        "event_type": row["event_type"],
                        "message": row["message"],
                        "metadata": md,
                        "created_at": _event_ts(row),
                    }
                )
                yield f"data: {data}\n\n"
            await asyncio.sleep(1.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")
