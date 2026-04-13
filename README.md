# Autonomous Media Buying Agent

An AI-powered media buying system that autonomously scouts publishers, negotiates ad placements via email, and generates hyper-contextual ad creatives — with zero manual labor.

## Business Model

Traditional ad buying means sitting at a desk buying inventory on Facebook or Google Ads. This agent replaces that entirely. Real-world e-commerce brands pay a monthly retainer (~$2,000/month) to run their ads. Instead of manual buying, the agent scours the internet, haggles directly with small publishers, and places hyper-contextual ads at a fraction of the cost — delivering 8× better CPM than AdSense while you do nothing.

---

## How It Works

The full pipeline runs autonomously once a campaign is created:

```
Client brief ingested (brand, budget, audience, seed URLs)
    ↓
Reconnaissance agent scrapes /ads.txt, contact pages, RSS feeds
    ↓
Publisher scorer ranks targets by remnant inventory likelihood
    ↓
Outreach agent generates personalized pitch email via Claude → sends via Gmail SMTP
    ↓
Gmail poller checks for replies every 30 seconds
    ↓
Claude classifies reply: approved / counter / rejected
    ↓
Approved → Creative pipeline generates ad copy + banner → sends delivery email
Counter  → Agent re-negotiates with counter-counter offer
Rejected → Moves to next publisher
    ↓
JS ad tag delivered → served → click tracked
```

---

## Tech Stack

**Backend**
- FastAPI (Python) — async API framework
- Supabase (Postgres) — database + storage
- Anthropic Claude — email generation, intent classification, ad copy
- OpenRouter — alternative LLM routing
- Gmail SMTP — outbound pitch emails
- IMAP polling — inbound reply detection
- Railway — backend hosting

**Frontend**
- Next.js (TypeScript)
- Tailwind CSS
- Server-Sent Events (SSE) — live agent activity stream
- Vercel — frontend hosting

---

## Project Structure

```
/
├── backend/
│   ├── app/
│   │   ├── main.py                    # FastAPI app + lifespan + CORS
│   │   ├── core/
│   │   │   └── database.py            # Supabase client
│   │   ├── models/
│   │   │   └── schemas.py             # Pydantic request/response models
│   │   ├── services/
│   │   │   └── recon.py               # Reconnaissance module
│   │   ├── agents/
│   │   │   ├── outreach.py            # Pitch email generation + sending
│   │   │   ├── gmail_poller.py        # IMAP reply polling loop
│   │   │   ├── creative.py            # Ad creative generation pipeline
│   │   │   └── helper.py             # Shared utilities (extract_json etc.)
│   │   ├── api/routes/
│   │   │   ├── campaigns.py           # Campaign CRUD + run + SSE stream
│   │   │   ├── publishers.py          # Publisher read endpoints
│   │   │   ├── recon.py               # Recon endpoints
│   │   │   └── webhook.py             # Inbound reply webhook
│   │   └── fixtures/
│   │       └── seed.py                # Demo data seeding
│   ├── requirements.txt
│   ├── Procfile                       # Railway start command
│   └── .env.example
└── frontend/
    ├── app/                           # Next.js app directory
    ├── components/                    # UI components
    └── lib/                           # API client + types
```

---

## Database Schema

Five tables auto-created on first server start:

| Table | Purpose |
|-------|---------|
| `campaigns` | Client briefs, budgets, status, spend tracking |
| `publishers` | Scraped publisher data, scores, contact emails |
| `outreach_logs` | Sent emails, replies, negotiation status |
| `ad_creatives` | Generated banners, click tracking IDs |
| `agent_events` | Live log of every agent action (powers SSE stream) |

---

## Publisher Scoring

Publishers are scored 0–7 based on remnant inventory likelihood:

| Signal | Points | Reason |
|--------|--------|--------|
| AdSense in ads.txt | +3 | High probability of remnant inventory |
| Traffic 10k–500k/day | +2 | Ideal size — big enough to matter, small enough to negotiate |
| No premium DSP listed | +2 | Not fully monetized, open to direct deals |

A score of 7/7 means the publisher is a perfect target. Sites like TechCrunch score low (2/7) because they use TradeDesk and DV360 — the agent deprioritizes them automatically.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| GET | `/health` | Health check |
| POST | `/api/campaigns/` | Create a new campaign |
| GET | `/api/campaigns/` | List all campaigns |
| GET | `/api/campaigns/{id}` | Get a single campaign |
| POST | `/api/campaigns/{id}/run` | Kick off the full agent pipeline |
| GET | `/api/campaigns/{id}/events` | SSE stream of live agent activity |
| POST | `/api/recon/` | Run recon on a single publisher URL |
| POST | `/api/recon/bulk` | Recon + rank multiple URLs |
| GET | `/api/publishers/` | List scored publishers (filterable by min_score) |
| GET | `/api/publishers/{id}` | Get a single publisher |
| POST | `/api/webhook/reply` | Inbound email reply webhook |

---

## Local Development

### Prerequisites
- Python 3.11+ (not 3.13 if using asyncpg)
- Node.js 18+
- A Supabase project
- Gmail account with IMAP enabled + App Password
- Anthropic API key

### Backend Setup

```bash
cd backend
python -m venv venv
source venv/bin/activate
pip install -r requirements.txt

cp .env.example .env
# Fill in your values (see Environment Variables section)

uvicorn app.main:app --reload
```

### Seed Demo Data

```bash
python -m app.fixtures.seed
```

This loads 3 dummy client campaigns and 3 pre-scored publishers (dev.to, lobste.rs, hackernoon.com) for demo use.

### Frontend Setup

```bash
cd frontend
npm install
cp .env.example .env.local
# Set NEXT_PUBLIC_API_BASE_URL=http://localhost:8000

npm run dev
```

---

## Environment Variables

### Backend (.env)

```
# Supabase
SUPABASE_URL=https://your-project.supabase.co
SUPABASE_SERVICE_ROLE_KEY=eyJ...

# Anthropic
ANTHROPIC_API_KEY=sk-ant-...

# OpenRouter (alternative LLM)
OPENROUTER_API_KEY=sk-or-...

# Gmail (outbound SMTP + inbound IMAP polling)
GMAIL_USER=your.agent@gmail.com
GMAIL_APP_PASSWORD=xxxx xxxx xxxx xxxx

# App config
PUBLIC_API_BASE=https://your-railway-app.up.railway.app
REPLY_POLL_INTERVAL=30
```

### Frontend (.env.local)

```
NEXT_PUBLIC_API_BASE_URL=https://your-railway-app.up.railway.app
```

---

## Gmail Setup

The agent uses Gmail for both sending pitch emails and detecting replies.

**Enable IMAP:**
Gmail → Settings → See all settings → Forwarding and POP/IMAP → Enable IMAP

**Generate App Password:**
myaccount.google.com → Security → 2-Step Verification → App Passwords → create one for "Mail"

**Two-account demo setup:**
- `agent@gmail.com` — the agent's sending account. Needs IMAP + App Password. Goes in `.env`.
- `publisher@gmail.com` — the dummy publisher inbox. Just a regular Gmail you log into manually and reply "Approved" from.

---

## Deployment

### Backend (Railway)

1. Push to GitHub
2. Create new Railway project → deploy from GitHub repo
3. Set **Root Directory** to `backend`
4. Add all environment variables in Railway → Variables
5. Railway auto-detects Python and uses `Procfile` to start the server

**Procfile:**
```
web: uvicorn app.main:app --host 0.0.0.0 --port $PORT
```

**Note:** Railway blocks outbound SMTP port 587. Use port 465 with `SMTP_SSL` instead.

### Frontend (Vercel)

```bash
cd frontend
vercel --prod
```

Set `NEXT_PUBLIC_API_BASE_URL` to your Railway domain in Vercel → Settings → Environment Variables. Redeploy after adding.

---

## Demo Flow

1. **Create a campaign** via the dashboard (client name, product, budget, seed URLs)
2. **Run the campaign** — agent reconnoiters seed URLs, scores publishers, sends pitch emails
3. **Watch the live feed** — SSE stream shows every agent action in real time
4. **Reply "Approved"** from the dummy publisher Gmail inbox
5. **Agent detects the reply** via Gmail poller → classifies as "approved"
6. **Creative pipeline fires** — Claude writes headline/CTA, generates banner, sends delivery email with ad tag
7. **Dashboard shows** spend, impressions, and 8× CPM improvement vs AdSense

---

## Key Demo Talking Points

- **Fully autonomous** — zero human intervention after campaign creation
- **Hyper-contextual** — ad copy is generated based on the publisher's trending articles
- **Direct deals** — bypasses Google/Facebook entirely, negotiates directly with publishers
- **Cost efficient** — targets remnant inventory at $0.50 CPM vs Google AdSense's $4.00 effective rate
- **Real emails** — judges see actual emails hitting real inboxes and triggering the agent
