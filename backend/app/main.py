from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio

from app.api.routes import campaigns, publishers, recon, webhook, ads
from app.api.routes.campaigns import events_router
from app.core.database import get_supabase


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Start Gmail reply poller in the background
    from app.agents.gmail_poller import start_poller
    sb = get_supabase()
    poller_task = asyncio.create_task(start_poller(sb))

    yield

    # Shut down poller cleanly on server stop
    poller_task.cancel()
    try:
        await poller_task
    except asyncio.CancelledError:
        pass


app = FastAPI(
    title="Autonomous Media Buying Agent",
    description="AI-powered programmatic ad buying via direct publisher outreach",
    version="0.1.0",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(publishers.router, prefix="/api/publishers", tags=["publishers"])
app.include_router(recon.router, prefix="/api/recon", tags=["recon"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["webhook"])
app.include_router(ads.router, prefix="/api/ads", tags=["ads"])
app.include_router(events_router, prefix="/api/events", tags=["events"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "media-buying-agent"}