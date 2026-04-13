import type {
  AgentEvent,
  AuditLogItem,
  Campaign,
  DeviceSession,
  NetworkNode,
  Publisher,
  SettingSection,
} from "@/lib/types";

export const mockCampaigns: Campaign[] = [
  {
    id: "c1f1dcb2-4d50-4a7d-a0e8-8edb4b61df11",
    client_name: "Quantum Leap Q4",
    product_desc: "Deep learning infrastructure demand generation for enterprise buyers.",
    budget: 50000,
    audience: "Enterprise architects, CTOs, DevOps leaders",
    seed_urls: ["https://theverge.com", "https://venturebeat.com"],
    status: "running",
    spend: 32450,
    impressions: 1200000,
    created_at: "2026-04-11T12:45:00.000Z",
    updated_at: "2026-04-12T10:22:00.000Z",
  },
  {
    id: "65cb4985-e24c-43c7-95ec-c4f2cbcc21e8",
    client_name: "Solaris Retargeting",
    product_desc: "Awareness and retargeting motion for premium cloud automation tools.",
    budget: 12000,
    audience: "Cloud platform buyers, RevOps, SaaS operators",
    seed_urls: ["https://wired.com", "https://techradar.com"],
    status: "draft",
    spend: 0,
    impressions: 0,
    created_at: "2026-04-10T08:15:00.000Z",
    updated_at: "2026-04-12T08:30:00.000Z",
  },
  {
    id: "67c363ea-2223-4d1d-9df4-1fb4407bdf29",
    client_name: "Brand Affinity X",
    product_desc: "Full-funnel media orchestration for a developer tools launch.",
    budget: 250000,
    audience: "Growth teams, startup founders, engineering managers",
    seed_urls: ["https://gizmodo.com", "https://adweek.com"],
    status: "running",
    spend: 88120,
    impressions: 8400000,
    created_at: "2026-04-02T09:10:00.000Z",
    updated_at: "2026-04-12T09:50:00.000Z",
  },
  {
    id: "cbfd5e04-95c4-43fa-98ec-2ccb365431b6",
    client_name: "Beta Test: Horizon",
    product_desc: "Developer adoption test across AI infrastructure channels.",
    budget: 5000,
    audience: "AI practitioners, MLOps engineers, platform leads",
    seed_urls: ["https://venturebeat.com"],
    status: "completed",
    spend: 5000,
    impressions: 450000,
    created_at: "2026-03-28T13:00:00.000Z",
    updated_at: "2026-04-05T16:10:00.000Z",
  },
];

export const mockLiveFeed: AgentEvent[] = [
  {
    id: "evt-01",
    event_type: "optimization",
    message:
      "ARCHITECT-09 redistributed $2,400 from low-performing CPM to high-conversion video assets in Quantum Leap Q4.",
    metadata: { severity: "success" },
    created_at: "2026-04-12T10:20:00.000Z",
  },
  {
    id: "evt-02",
    event_type: "bid_alert",
    message:
      "Winning bid lock achieved on premium inventory: Financial Times homepage masthead.",
    metadata: { severity: "live" },
    created_at: "2026-04-12T10:05:00.000Z",
  },
  {
    id: "evt-03",
    event_type: "recon",
    message:
      "Metadata extraction complete for domain compute-cloud.io. Identified four key decision makers.",
    metadata: { severity: "info" },
    created_at: "2026-04-12T09:58:00.000Z",
  },
  {
    id: "evt-04",
    event_type: "scan",
    message:
      "System ping: URL https://cloud-architect.org/news verified for safety and queued for deeper scoring.",
    metadata: { severity: "info" },
    created_at: "2026-04-12T09:43:00.000Z",
  },
];

export const mockPublishers: Publisher[] = [
  {
    id: "pub-01",
    url: "https://theverge.com",
    contact_email: "partnerships@theverge.com",
    ad_networks: ["Google Ad Manager", "Direct"],
    estimated_traffic: "42.8M",
    score: 94,
    has_adsense: true,
    has_premium_dsp: true,
    trending_headlines: ["AI chips reshape cloud budgets", "Browser wars return"],
    created_at: "2026-04-10T12:15:00.000Z",
  },
  {
    id: "pub-02",
    url: "https://wired.com",
    contact_email: "adsales@wired.com",
    ad_networks: ["Google Ad Manager", "Programmatic Direct"],
    estimated_traffic: "19.5M",
    score: 88,
    has_adsense: true,
    has_premium_dsp: true,
    trending_headlines: ["Autonomous agents enter media buying"],
    created_at: "2026-04-09T12:15:00.000Z",
  },
  {
    id: "pub-03",
    url: "https://techradar.com",
    contact_email: "media@techradar.com",
    ad_networks: ["Google Ad Manager"],
    estimated_traffic: "31.2M",
    score: 76,
    has_adsense: true,
    has_premium_dsp: false,
    trending_headlines: ["GPU prices flatten after new launch cycle"],
    created_at: "2026-04-08T12:15:00.000Z",
  },
];

export const analyticsTimeline = [
  { label: "01 Oct", spend: 220, roas: 3.8 },
  { label: "10 Oct", spend: 480, roas: 4.6 },
  { label: "20 Oct", spend: 610, roas: 5.1 },
  { label: "30 Oct", spend: 540, roas: 5.4 },
];

export const analyticsActions = [
  ["12:45:01", "X-RAY_01", "Bid Optimization +15%", "$4.20", "6.2x", "COMPLETED"],
  ["12:44:58", "OMEGA_V3", "Audience Pivot (Tier 1)", "$12.50", "4.8x", "COMPLETED"],
  ["12:44:52", "X-RAY_01", "Creative A/B Switch", "$3.80", "3.1x", "PROCESSING"],
];

export const networkNodes: NetworkNode[] = [
  {
    id: "JP_TYO_042",
    region: "Tokyo",
    latency_ms: 14,
    bidding_load: "4.2M req/sec",
    status: "active",
    coordinates: "35.6762° N, 139.6503° E",
    note: "Premium finance inventory detected with high-intent momentum.",
  },
  {
    id: "UK_LDN_008",
    region: "London",
    latency_ms: 18,
    bidding_load: "3.4M req/sec",
    status: "active",
    coordinates: "51.5072° N, 0.1276° W",
    note: "CPM volatility spike being offset by adaptive floor logic.",
  },
  {
    id: "SG_CORE_011",
    region: "Singapore",
    latency_ms: 5,
    bidding_load: "2.6M req/sec",
    status: "stealth",
    coordinates: "1.3521° N, 103.8198° E",
    note: "All clusters reporting sub-5ms internal latency.",
  },
  {
    id: "NY_EST_002",
    region: "New York",
    latency_ms: 23,
    bidding_load: "1.9M req/sec",
    status: "standby",
    coordinates: "40.7128° N, 74.0060° W",
    note: "Scheduled maintenance; traffic routed to backup nodes.",
  },
];

export const settingSections: SettingSection[] = [
  {
    title: "Threshold Logic & Scoring",
    description: "Core autonomous controls that govern execution confidence and scrape cadence.",
    items: [
      {
        label: "Confidence Floor",
        value: "75.4%",
        hint: "Minimum probability score required for autonomous execution.",
        status: "live",
      },
      {
        label: "Scrape Frequency",
        value: "Every 15 minutes",
        hint: "Publisher polling cadence for standard operations.",
      },
      {
        label: "Budget Surge Limit",
        value: "$1,500 / hr",
        hint: "Maximum budget acceleration when conversion momentum rises.",
      },
    ],
  },
  {
    title: "Integrations",
    description: "Operational services supporting outbound communications and orchestration.",
    items: [
      {
        label: "Resend",
        value: "Transactional Email & Alerts",
        hint: "Ready for outbound outreach and webhook replies.",
        status: "connected",
      },
      {
        label: "FastAPI",
        value: "Internal Logic Connector",
        hint: "Primary backend used by the dashboard routes in this repo.",
        status: "connected",
      },
      {
        label: "Stripe",
        value: "Billing & Payouts",
        hint: "Design placeholder until billing support is added.",
        status: "warning",
      },
    ],
  },
];

export const auditLogItems: AuditLogItem[] = [
  {
    id: "audit-01",
    timestamp: "2026-04-12 14:22:01",
    agent_id: "BID_UNIT_09",
    action_type: "BID_LOCK",
    status: "COMMITTED",
    data_hash: "0x7f4a...9b12",
    raw: "LOCK_BID on premium finance cluster",
  },
  {
    id: "audit-02",
    timestamp: "2026-04-12 14:21:58",
    agent_id: "RECON_ALPHA",
    action_type: "RECON_START",
    status: "PROCESSING",
    data_hash: "0x3c12...4e88",
    raw: "Publisher metadata scrape queued",
  },
  {
    id: "audit-03",
    timestamp: "2026-04-12 14:21:45",
    agent_id: "CREATIVE_HIVE",
    action_type: "CREATIVE_GEN",
    status: "RETRIABLE_FAIL",
    data_hash: "0x99a1...11f0",
    raw: "Creative generation retried after timeout",
  },
];

export const operatorSessions: DeviceSession[] = [
  {
    name: "Neural-Link Workstation",
    location: "London, UK",
    ipAddress: "192.168.4.201",
    lastActivity: "Current session",
    status: "ACTIVE",
  },
  {
    name: "Secure Handheld Hub",
    location: "London, UK",
    ipAddress: "84.22.112.9",
    lastActivity: "14 mins ago",
    status: "CONNECTED",
  },
  {
    name: "Tactical Pad Alpha",
    location: "Berlin, DE",
    ipAddress: "10.0.0.45",
    lastActivity: "2 hours ago",
    status: "IDLE",
  },
];

export const topLeaders = [
  { name: "AD_STRAT_GLOBAL", conversions: "42.4k", note: "Highest conversion velocity" },
  { name: "PRIME_STREAM_NET", conversions: "38.1k", note: "Stable premium inventory" },
  { name: "VORTEX_MEDIA_IA", conversions: "29.8k", note: "Strong retargeting return" },
  { name: "SKY_NETWORK_7", conversions: "12.2k", note: "Candidate for spend reduction" },
];

export function formatCurrency(value: number) {
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

export function formatCompact(value: number) {
  return new Intl.NumberFormat("en-US", {
    notation: "compact",
    maximumFractionDigits: 1,
  }).format(value);
}

export function getStatusTone(status: string) {
  const normalized = status.toLowerCase();
  if (normalized.includes("run") || normalized.includes("active") || normalized.includes("live")) {
    return "live";
  }
  if (normalized.includes("draft") || normalized.includes("processing")) {
    return "warning";
  }
  if (normalized.includes("fail") || normalized.includes("critical")) {
    return "danger";
  }
  return "neutral";
}
