import os
import asyncpg
from typing import AsyncGenerator

DATABASE_URL = os.environ.get("DATABASE_URL", "postgresql://postgres:password@localhost:5432/mediabuy")

_pool: asyncpg.Pool | None = None


async def get_pool() -> asyncpg.Pool:
    global _pool
    if _pool is None:
        _pool = await asyncpg.create_pool(DATABASE_URL, min_size=2, max_size=10)
    return _pool


async def get_db() -> AsyncGenerator[asyncpg.Connection, None]:
    pool = await get_pool()
    async with pool.acquire() as conn:
        yield conn


async def create_tables():
    pool = await get_pool()
    async with pool.acquire() as conn:
        await conn.execute("""
            CREATE TABLE IF NOT EXISTS campaigns (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                client_name TEXT NOT NULL,
                product_desc TEXT NOT NULL,
                budget      INTEGER NOT NULL,         -- in dollars
                audience    TEXT NOT NULL,
                seed_urls   TEXT[] NOT NULL DEFAULT '{}',
                status      TEXT NOT NULL DEFAULT 'pending',  -- pending | running | paused | complete
                spend       INTEGER NOT NULL DEFAULT 0,
                impressions INTEGER NOT NULL DEFAULT 0,
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS publishers (
                id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                url              TEXT NOT NULL UNIQUE,
                contact_email    TEXT,
                ad_networks      TEXT[] DEFAULT '{}',
                estimated_traffic TEXT,
                score            INTEGER NOT NULL DEFAULT 0,
                has_adsense      BOOLEAN DEFAULT FALSE,
                has_premium_dsp  BOOLEAN DEFAULT FALSE,
                trending_headlines TEXT[] DEFAULT '{}',
                created_at       TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS outreach_logs (
                id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                campaign_id    UUID NOT NULL REFERENCES campaigns(id),
                publisher_id   UUID NOT NULL REFERENCES publishers(id),
                offer_amount   INTEGER NOT NULL,        -- in dollars
                email_subject  TEXT,
                email_body     TEXT,
                resend_id      TEXT,                    -- Resend message ID
                status         TEXT NOT NULL DEFAULT 'sent',  -- sent | approved | rejected | countered | negotiating
                reply_raw      TEXT,
                reply_intent   TEXT,                    -- approved | rejected | counter
                counter_amount INTEGER,
                created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW(),
                replied_at     TIMESTAMPTZ
            );

            CREATE TABLE IF NOT EXISTS ad_creatives (
                id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                campaign_id    UUID NOT NULL REFERENCES campaigns(id),
                outreach_id    UUID REFERENCES outreach_logs(id),
                headline       TEXT NOT NULL,
                subheadline    TEXT,
                cta            TEXT,
                image_url      TEXT,
                banner_url     TEXT,
                click_track_id TEXT UNIQUE,
                clicks         INTEGER NOT NULL DEFAULT 0,
                created_at     TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );

            CREATE TABLE IF NOT EXISTS agent_events (
                id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
                campaign_id UUID REFERENCES campaigns(id),
                event_type  TEXT NOT NULL,             -- recon | score | outreach | reply | creative | click
                message     TEXT NOT NULL,
                metadata    JSONB DEFAULT '{}',
                created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
            );
        """)
        print("✅ Tables created/verified")