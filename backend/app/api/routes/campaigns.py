from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import StreamingResponse
import asyncpg
import json
import asyncio
from uuid import UUID

from app.core.database import get_db
from app.models.schemas import CampaignCreate, CampaignOut

router = APIRouter()


@router.post("/", response_model=CampaignOut, status_code=201)
async def create_campaign(payload: CampaignCreate, db: asyncpg.Connection = Depends(get_db)):
    row = await db.fetchrow(
        """
        INSERT INTO campaigns (client_name, product_desc, budget, audience, seed_urls)
        VALUES ($1, $2, $3, $4, $5)
        RETURNING *
        """,
        payload.client_name,
        payload.product_desc,
        payload.budget,
        payload.audience,
        payload.seed_urls,
    )
    return dict(row)


@router.get("/", response_model=list[CampaignOut])
async def list_campaigns(db: asyncpg.Connection = Depends(get_db)):
    rows = await db.fetch("SELECT * FROM campaigns ORDER BY created_at DESC")
    return [dict(r) for r in rows]


@router.get("/{campaign_id}", response_model=CampaignOut)
async def get_campaign(campaign_id: UUID, db: asyncpg.Connection = Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM campaigns WHERE id = $1", campaign_id)
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    return dict(row)


@router.post("/{campaign_id}/run", status_code=202)
async def run_campaign(campaign_id: UUID, db: asyncpg.Connection = Depends(get_db)):
    """
    Kick off the full agent pipeline for a campaign.
    Updates status to 'running' and queues background work.
    In prod you'd hand this to a task queue (Celery, ARQ, etc).
    """
    row = await db.fetchrow("SELECT * FROM campaigns WHERE id = $1", campaign_id)
    if not row:
        raise HTTPException(status_code=404, detail="Campaign not found")
    if row["status"] == "running":
        raise HTTPException(status_code=409, detail="Campaign already running")

    await db.execute(
        "UPDATE campaigns SET status = 'running', updated_at = NOW() WHERE id = $1",
        campaign_id,
    )
    # TODO: enqueue pipeline task → recon → score → outreach
    return {"message": "Campaign started", "campaign_id": str(campaign_id)}


@router.get("/{campaign_id}/events")
async def campaign_events_stream(campaign_id: UUID, db: asyncpg.Connection = Depends(get_db)):
    """
    Server-Sent Events stream of agent_events for live dashboard feed.
    Frontend connects once; events push in real time.
    """
    async def event_generator():
        last_id = None
        while True:
            if last_id is None:
                rows = await db.fetch(
                    "SELECT * FROM agent_events WHERE campaign_id = $1 ORDER BY created_at ASC",
                    campaign_id,
                )
            else:
                rows = await db.fetch(
                    "SELECT * FROM agent_events WHERE campaign_id = $1 AND id > $2 ORDER BY created_at ASC",
                    campaign_id, last_id,
                )
            for row in rows:
                last_id = row["id"]
                data = json.dumps({
                    "id": str(row["id"]),
                    "event_type": row["event_type"],
                    "message": row["message"],
                    "metadata": dict(row["metadata"]) if row["metadata"] else {},
                    "created_at": row["created_at"].isoformat(),
                })
                yield f"data: {data}\n\n"
            await asyncio.sleep(1.5)

    return StreamingResponse(event_generator(), media_type="text/event-stream")