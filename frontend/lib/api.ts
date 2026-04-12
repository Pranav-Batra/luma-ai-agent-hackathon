import type {
  AgentEvent,
  Campaign,
  CampaignCreateInput,
  Publisher,
  ReconResult,
} from "@/lib/types";

const API_BASE_URL =
  process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://127.0.0.1:8000";

async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T | null> {
  try {
    const response = await fetch(`${API_BASE_URL}${path}`, {
      ...init,
      headers: {
        "Content-Type": "application/json",
        ...(init?.headers ?? {}),
      },
      cache: "no-store",
    });

    if (!response.ok) {
      return null;
    }

    return (await response.json()) as T;
  } catch {
    return null;
  }
}

export function getCampaignEventsUrl(campaignId: string) {
  return `${API_BASE_URL}/api/campaigns/${campaignId}/events`;
}

export function getApiBaseUrl() {
  return API_BASE_URL;
}

export async function getCampaigns() {
  return apiFetch<Campaign[]>("/api/campaigns/");
}

export async function getCampaign(campaignId: string) {
  return apiFetch<Campaign>(`/api/campaigns/${campaignId}`);
}

export async function createCampaign(payload: CampaignCreateInput) {
  return apiFetch<Campaign>("/api/campaigns/", {
    method: "POST",
    body: JSON.stringify(payload),
  });
}

export async function runCampaign(campaignId: string) {
  return apiFetch<{ message: string; campaign_id: string }>(
    `/api/campaigns/${campaignId}/run`,
    {
      method: "POST",
      body: JSON.stringify({}),
    },
  );
}

export async function getPublishers(minScore = 0) {
  return apiFetch<Publisher[]>(
    `/api/publishers/?min_score=${encodeURIComponent(String(minScore))}`,
  );
}

export async function runRecon(url: string, campaignId?: string) {
  return apiFetch<ReconResult>("/api/recon/", {
    method: "POST",
    body: JSON.stringify({
      url,
      campaign_id: campaignId ?? null,
    }),
  });
}

export async function runBulkRecon(urls: string[], campaignId?: string) {
  return apiFetch<{ publishers: ReconResult[]; total: number }>("/api/recon/bulk", {
    method: "POST",
    body: JSON.stringify({
      urls,
      campaign_id: campaignId ?? null,
    }),
  });
}

export function normalizeEvent(input: AgentEvent): AgentEvent {
  return {
    id: input.id,
    event_type: input.event_type,
    message: input.message,
    metadata: input.metadata ?? {},
    created_at: input.created_at,
  };
}
