-- Run this once in Supabase: SQL Editor → New query → Run.
-- The Python app uses the Supabase REST client (no raw Postgres URL required).

create extension if not exists "pgcrypto";

create table if not exists campaigns (
    id          uuid primary key default gen_random_uuid(),
    client_name text not null,
    product_desc text not null,
    budget      integer not null,
    audience    text not null,
    seed_urls   text[] not null default '{}',
    status      text not null default 'pending',
    spend       integer not null default 0,
    impressions integer not null default 0,
    created_at  timestamptz not null default now(),
    updated_at  timestamptz not null default now()
);

create table if not exists publishers (
    id               uuid primary key default gen_random_uuid(),
    url              text not null unique,
    contact_email    text,
    ad_networks      text[] default '{}',
    estimated_traffic text,
    score            integer not null default 0,
    has_adsense      boolean default false,
    has_premium_dsp  boolean default false,
    trending_headlines text[] default '{}',
    created_at       timestamptz not null default now()
);

create table if not exists outreach_logs (
    id             uuid primary key default gen_random_uuid(),
    campaign_id    uuid not null references campaigns(id) on delete cascade,
    publisher_id   uuid not null references publishers(id) on delete cascade,
    offer_amount   integer not null,
    email_subject  text,
    email_body     text,
    resend_id      text,
    status         text not null default 'sent',
    reply_raw      text,
    reply_intent   text,
    counter_amount integer,
    created_at     timestamptz not null default now(),
    replied_at     timestamptz
);

create table if not exists ad_creatives (
    id             uuid primary key default gen_random_uuid(),
    campaign_id    uuid not null references campaigns(id) on delete cascade,
    outreach_id    uuid references outreach_logs(id) on delete set null,
    headline       text not null,
    subheadline    text,
    cta            text,
    image_url      text,
    banner_url     text,
    click_track_id text unique,
    clicks         integer not null default 0,
    created_at     timestamptz not null default now()
);

create table if not exists agent_events (
    id          uuid primary key default gen_random_uuid(),
    campaign_id uuid references campaigns(id) on delete cascade,
    event_type  text not null,
    message     text not null,
    metadata    jsonb default '{}',
    created_at  timestamptz not null default now()
);

-- Backend uses the service role key; RLS optional. Enable if you switch to anon key:
-- alter table campaigns enable row level security;
