"""
Demo fixtures — pre-written JSON profiles for hackathon demo.
Load these via: python -m app.fixtures.seed
"""

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


async def seed_db():
    """Seed the database with demo fixtures."""
    from app.core.database import get_pool
    pool = await get_pool()
    async with pool.acquire() as conn:
        # Seed publishers
        for pub in DUMMY_PUBLISHERS:
            await conn.execute(
                """
                INSERT INTO publishers (url, contact_email, ad_networks, estimated_traffic,
                                        has_adsense, has_premium_dsp, trending_headlines, score)
                VALUES ($1,$2,$3,$4,$5,$6,$7,$8)
                ON CONFLICT (url) DO NOTHING
                """,
                pub["url"], pub["contact_email"], pub["ad_networks"],
                pub["estimated_traffic"], pub["has_adsense"], pub["has_premium_dsp"],
                pub["trending_headlines"], pub["score"],
            )
        print(f"✅ Seeded {len(DUMMY_PUBLISHERS)} publishers")

        # Seed campaigns
        for client in DUMMY_CLIENTS:
            await conn.execute(
                """
                INSERT INTO campaigns (client_name, product_desc, budget, audience, seed_urls)
                VALUES ($1,$2,$3,$4,$5)
                ON CONFLICT DO NOTHING
                """,
                client["client_name"], client["product_desc"],
                client["budget"], client["audience"], client["seed_urls"],
            )
        print(f"✅ Seeded {len(DUMMY_CLIENTS)} campaigns")


if __name__ == "__main__":
    import asyncio
    asyncio.run(seed_db())