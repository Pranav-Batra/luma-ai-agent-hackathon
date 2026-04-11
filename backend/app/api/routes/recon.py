from fastapi import APIRouter, Depends, BackgroundTasks
from uuid import UUID
import asyncpg

from app.core.database import get_db
from app.models.schemas import ReconRequest, ReconResult
from app.services.recon import run_recon

router = APIRouter()


@router.post("/", response_model=ReconResult)
async def recon_publisher(
    payload: ReconRequest,
    background_tasks: BackgroundTasks,
    db: asyncpg.Connection = Depends(get_db),
):
    """
    Run recon on a single publisher URL.
    Upserts the publisher into the DB and logs an agent_event.
    """
    result = await run_recon(payload.url)

    # Upsert publisher record
    pub_row = await db.fetchrow(
        """
        INSERT INTO publishers (url, contact_email, ad_networks, estimated_traffic,
                                has_adsense, has_premium_dsp, trending_headlines, score)
        VALUES ($1, $2, $3, $4, $5, $6, $7, $8)
        ON CONFLICT (url) DO UPDATE
            SET contact_email      = EXCLUDED.contact_email,
                ad_networks        = EXCLUDED.ad_networks,
                estimated_traffic  = EXCLUDED.estimated_traffic,
                has_adsense        = EXCLUDED.has_adsense,
                has_premium_dsp    = EXCLUDED.has_premium_dsp,
                trending_headlines = EXCLUDED.trending_headlines,
                score              = EXCLUDED.score
        RETURNING id
        """,
        result["url"],
        result.get("contact_email"),
        result.get("ad_networks", []),
        result.get("estimated_traffic", "unknown"),
        result.get("has_adsense", False),
        result.get("has_premium_dsp", False),
        result.get("trending_headlines", []),
        result.get("score", 0),
    )

    # Log agent event if tied to a campaign
    if payload.campaign_id:
        await db.execute(
            """
            INSERT INTO agent_events (campaign_id, event_type, message, metadata)
            VALUES ($1, 'recon', $2, $3::jsonb)
            """,
            payload.campaign_id,
            f"Scanned {result['url']} — score {result['score']}/7, contact: {result.get('contact_email', 'not found')}",
            f'{{"publisher_id": "{pub_row["id"]}", "score": {result["score"]}}}',
        )

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
    db: asyncpg.Connection = Depends(get_db),
):
    """Run recon on multiple seed URLs and return ranked publisher list."""
    import asyncio
    tasks = [run_recon(url) for url in urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)

    publishers = []
    for r in results:
        if isinstance(r, Exception):
            continue
        publishers.append(r)

    # Sort by score descending
    publishers.sort(key=lambda x: x.get("score", 0), reverse=True)
    return {"publishers": publishers, "total": len(publishers)}