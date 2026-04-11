from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.api.routes import campaigns, publishers, recon, webhook

app = FastAPI(
    title="Autonomous Media Buying Agent",
    description="AI-powered programmatic ad buying via direct publisher outreach",
    version="0.1.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # tighten this in prod
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(campaigns.router, prefix="/api/campaigns", tags=["campaigns"])
app.include_router(publishers.router, prefix="/api/publishers", tags=["publishers"])
app.include_router(recon.router, prefix="/api/recon", tags=["recon"])
app.include_router(webhook.router, prefix="/api/webhook", tags=["webhook"])


@app.get("/health")
async def health():
    return {"status": "ok", "service": "media-buying-agent"}
