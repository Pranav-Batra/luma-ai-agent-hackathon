"""
Demo fixtures — pre-written JSON profiles for hackathon demo.
Load via: cd backend && PYTHONPATH=. python -m app.fixtures.seed

Requires SUPABASE_URL and SUPABASE_SERVICE_ROLE_KEY.
"""

from app.core.database import get_supabase

DUMMY_CLIENTS = [
    {
        "client_name": "MechKeys Pro",
        "product_desc": "Premium mechanical keyboards for developers and enthusiasts. Cherry MX switches, aluminum frames, programmable via QMK.",
        "budget": 500,
        "audience": "developers, keyboard enthusiasts, power users",
        "seed_urls": ["dev.to", "lobste.rs", "hackernoon.com"],
    },
    {
        "client_name": "DeployBot",
        "product_desc": "One-click deployment platform for indie hackers. GitHub integration, zero-config, $9/month.",
        "budget": 300,
        "audience": "indie hackers, solo developers, startup founders",
        "seed_urls": ["dev.to", "hackernoon.com"],
    },
    {
        "client_name": "PixelPerfect AI",
        "product_desc": "AI-powered design tool that converts Figma mockups to production React code in seconds.",
        "budget": 800,
        "audience": "frontend developers, designers, product teams",
        "seed_urls": ["dev.to", "lobste.rs"],
    },
]

DUMMY_PUBLISHERS = [
    {
        "url": "https://dev.to",
        "contact_email": "ads@dev.to",
        "ad_networks": ["AdSense", "Carbon Ads"],
        "estimated_traffic": "80k/day",
        "has_adsense": True,
        "has_premium_dsp": False,
        "score": 7,
        "trending_headlines": [
            "Why I switched from React to htmx",
            "Building a RAG pipeline in 100 lines of Python",
            "Stop over-engineering your side projects",
        ],
    },
    {
        "url": "https://lobste.rs",
        "contact_email": "ads@lobste.rs",
        "ad_networks": ["AdSense"],
        "estimated_traffic": "30k/day",
        "has_adsense": True,
        "has_premium_dsp": False,
        "score": 7,
        "trending_headlines": [
            "Ask Lobsters: Best terminal emulator in 2025?",
            "Zig 0.13 released with new async model",
            "How Cloudflare handles 50M req/s",
        ],
    },
    {
        "url": "https://hackernoon.com",
        "contact_email": "sponsor@hackernoon.com",
        "ad_networks": ["AdSense", "Carbon"],
        "estimated_traffic": "120k/day",
        "has_adsense": True,
        "has_premium_dsp": False,
        "score": 7,
        "trending_headlines": [
            "The death of the junior developer",
            "Rust is eating Python's lunch in ML tooling",
            "Why every startup should build on Postgres",
        ],
    },
]


def seed_db() -> None:
    """Seed the database with demo fixtures."""
    sb = get_supabase()

    for pub in DUMMY_PUBLISHERS:
        sb.table("publishers").upsert(pub, on_conflict="url").execute()
    print(f"✅ Seeded {len(DUMMY_PUBLISHERS)} publishers")

    for client in DUMMY_CLIENTS:
        sb.table("campaigns").insert(
            {
                "client_name": client["client_name"],
                "product_desc": client["product_desc"],
                "budget": client["budget"],
                "audience": client["audience"],
                "seed_urls": client["seed_urls"],
            }
        ).execute()
    print(f"✅ Seeded {len(DUMMY_CLIENTS)} campaigns")


if __name__ == "__main__":
    seed_db()
