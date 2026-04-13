"""
Click tracking for ad_creatives: increment clicks and redirect to destination.
"""

import asyncio
import os

from fastapi import APIRouter, Depends, HTTPException
from fastapi.responses import RedirectResponse
from supabase import Client

from app.core.database import get_supabase

router = APIRouter()

DEFAULT_DESTINATION = os.environ.get("DEFAULT_AD_DESTINATION", "https://example.com")


def _increment_click(sb: Client, click_track_id: str) -> bool:
    r = (
        sb.table("ad_creatives")
        .select("id, campaign_id, clicks")
        .eq("click_track_id", click_track_id)
        .limit(1)
        .execute()
    )
    if not r.data:
        return False
    row = r.data[0]
    new_clicks = int(row.get("clicks") or 0) + 1
    sb.table("ad_creatives").update({"clicks": new_clicks}).eq("click_track_id", click_track_id).execute()

    cid = row.get("campaign_id")
    if cid:
        sb.table("agent_events").insert(
            {
                "campaign_id": str(cid),
                "event_type": "click",
                "message": f"Banner click (track {click_track_id[:8]}…)",
                "metadata": {"click_track_id": click_track_id, "ad_creative_id": row["id"]},
            }
        ).execute()
    return True


@router.get("/{click_track_id}/click")
async def track_click(
    click_track_id: str,
    dest: str | None = None,
    sb: Client = Depends(get_supabase),
):
    """
    Record a click on the tracked URL, then 302 redirect.
    Query `dest` overrides the default landing page when you want A/B tests later.
    """
    ok = await asyncio.to_thread(_increment_click, sb, click_track_id)
    if not ok:
        raise HTTPException(status_code=404, detail="Unknown click id")

    target = dest or DEFAULT_DESTINATION
    return RedirectResponse(url=target, status_code=302)
