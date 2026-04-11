from fastapi import APIRouter, Depends, HTTPException
from uuid import UUID
import asyncpg

from app.core.database import get_db
from app.models.schemas import PublisherOut

router = APIRouter()


@router.get("/", response_model=list[PublisherOut])
async def list_publishers(
    min_score: int = 0,
    db: asyncpg.Connection = Depends(get_db),
):
    rows = await db.fetch(
        "SELECT * FROM publishers WHERE score >= $1 ORDER BY score DESC",
        min_score,
    )
    return [dict(r) for r in rows]


@router.get("/{publisher_id}", response_model=PublisherOut)
async def get_publisher(publisher_id: UUID, db: asyncpg.Connection = Depends(get_db)):
    row = await db.fetchrow("SELECT * FROM publishers WHERE id = $1", publisher_id)
    if not row:
        raise HTTPException(status_code=404, detail="Publisher not found")
    return dict(row)