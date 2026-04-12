from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
import asyncio

from supabase import Client

from app.core.database import get_supabase
from app.models.schemas import PublisherOut

router = APIRouter()


def _list_publishers(sb: Client, min_score: int) -> list[dict]:
    r = (
        sb.table("publishers")
        .select("*")
        .gte("score", min_score)
        .order("score", desc=True)
        .execute()
    )
    return r.data or []


@router.get("/", response_model=list[PublisherOut])
async def list_publishers(
    min_score: int = 0,
    sb: Client = Depends(get_supabase),
):
    return await asyncio.to_thread(_list_publishers, sb, min_score)


def _get_publisher(sb: Client, publisher_id: UUID) -> dict | None:
    r = sb.table("publishers").select("*").eq("id", str(publisher_id)).limit(1).execute()
    if not r.data:
        return None
    return r.data[0]


@router.get("/{publisher_id}", response_model=PublisherOut)
async def get_publisher(publisher_id: UUID, sb: Client = Depends(get_supabase)):
    row = await asyncio.to_thread(_get_publisher, sb, publisher_id)
    if not row:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return row
