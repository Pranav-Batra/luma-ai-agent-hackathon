import asyncio
from uuid import UUID

from fastapi import APIRouter, Depends
from supabase import Client

from app.core.database import get_supabase
from app.models.schemas import ReconRequest, ReconResult
from app.services.recon import run_recon

router = APIRouter()


def _upsert_publisher(sb, result: dict) -> str:
    row = {
        "url": result["url"],
        "contact_email": result.get("contact_email"),
        "ad_networks": result.get("ad_networks", []),
        "estimated_traffic": result.get("estimated_traffic", "unknown"),
        "has_adsense": result.get("has_adsense", False),
        "has_premium_dsp": result.get("has_premium_dsp", False),
        "trending_headlines": result.get("trending_headlines", []),
        "score": result.get("score", 0),
    }
    r = sb.table("publishers").upsert(row, on_conflict="url").select("id").execute()
    if not r.data:
        raise RuntimeError("publisher upsert returned no data")
    return r.data[0]["id"]


def _insert_recon_event(sb, campaign_id: UUID, result: dict, publisher_id: str) -> None:
    sb.table("agent_events").insert(
        {
            "campaign_id": str(campaign_id),
            "event_type": "recon",
            "message": (
                f"Scanned {result['url']} — score {result['score']}/7, contact: "
                f"{result.get('contact_email') or 'not found'}"
            ),
            "metadata": {"publisher_id": publisher_id, "score": result["score"]},
        }
    ).execute()


@router.post("/", response_model=ReconResult)
async def recon_publisher(
    payload: ReconRequest,
    sb: Client = Depends(get_supabase),
):
    """
    Run recon on a single publisher URL.
    Upserts the publisher into the DB and logs an agent_event.
    """
    result = await run_recon(payload.url)

    pub_id = await asyncio.to_thread(_upsert_publisher, sb, result)

    if payload.campaign_id:
        await asyncio.to_thread(_insert_recon_event, sb, payload.campaign_id, result, pub_id)

    return ReconResult(
        url=result["url"],
        ad_networks=result.get("ad_networks", []),
        contact_email=result.get("contact_email"),
        estimated_traffic=result.get("estimated_traffic", "unknown"),
        has_adsense=result.get("has_adsense", False),
        has_premium_dsp=result.get("has_premium_dsp", False),
        trending_headlines=result.get("trending_headlines", []),
        score=result.get("score", 0),
    )


@router.post("/bulk")
async def recon_bulk(
    urls: list[str],
    campaign_id: UUID | None = None,
):
    """Run recon on multiple seed URLs and return ranked publisher list."""
    tasks = [run_recon(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    publishers = []
    for r in results:
        if isinstance(r, Exception):
            continue
        publishers.append(r)

    publishers.sort(key=lambda x: x.get("score", 0), reverse=True)
    return {"publishers": publishers, "total": len(publishers)}
