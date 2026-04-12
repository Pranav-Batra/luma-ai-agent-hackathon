export interface Campaign {
  id: string;
  client_name: string;
  product_desc: string;
  budget: number;
  audience: string;
  seed_urls: string[];
  status: string;
  spend: number;
  impressions: number;
  created_at: string;
  updated_at: string;
}

export interface Publisher {
  id: string;
  url: string;
  contact_email: string | null;
  ad_networks: string[];
  estimated_traffic: string | null;
  score: number;
  has_adsense: boolean;
  has_premium_dsp: boolean;
  trending_headlines: string[];
  created_at: string;
}

export interface ReconResult {
  url: string;
  ad_networks: string[];
  contact_email: string | null;
  estimated_traffic: string;
  has_adsense: boolean;
  has_premium_dsp: boolean;
  trending_headlines: string[];
  score: number;
}

export interface CampaignCreateInput {
  client_name: string;
  product_desc: string;
  budget: number;
  audience: string;
  seed_urls: string[];
}

export interface AgentEvent {
  id: string;
  event_type: string;
  message: string;
  metadata: Record<string, string | number | boolean>;
  created_at: string;
}

export interface AuditLogItem {
  id: string;
  timestamp: string;
  agent_id: string;
  action_type: string;
  status: string;
  data_hash: string;
  raw: string;
}

export interface NetworkNode {
  id: string;
  region: string;
  latency_ms: number;
  bidding_load: string;
  status: "active" | "stealth" | "standby";
  coordinates: string;
  note: string;
}

export interface SettingSection {
  title: string;
  description: string;
  items: Array<{
    label: string;
    value: string;
    hint: string;
    status?: "connected" | "warning" | "live";
  }>;
}

export interface DeviceSession {
  name: string;
  location: string;
  ipAddress: string;
  lastActivity: string;
  status: string;
}
