import { afterEach, describe, expect, it, vi } from "vitest";

import {
  createCampaign,
  getCampaignEventsUrl,
  normalizeEvent,
  runRecon,
} from "@/lib/api";

describe("api helpers", () => {
  afterEach(() => {
    vi.restoreAllMocks();
  });

  it("builds the SSE endpoint URL for a campaign", () => {
    expect(getCampaignEventsUrl("abc-123")).toBe(
      "http://127.0.0.1:8000/api/campaigns/abc-123/events",
    );
  });

  it("normalizes event payloads with fallback metadata", () => {
    expect(
      normalizeEvent({
        id: "evt-1",
        event_type: "reply",
        message: "Reply received",
        metadata: {} as Record<string, string | number | boolean>,
        created_at: "2026-04-12T10:00:00.000Z",
      }),
    ).toEqual({
      id: "evt-1",
      event_type: "reply",
      message: "Reply received",
      metadata: {},
      created_at: "2026-04-12T10:00:00.000Z",
    });
  });

  it("posts campaign creation payloads to the backend", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({ id: "campaign-123" }),
    } as Response);

    await createCampaign({
      client_name: "Quantum Leap Q4",
      product_desc: "Deep learning infrastructure demand generation",
      budget: 5000,
      audience: "Enterprise architects",
      seed_urls: ["https://theverge.com"],
    });

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/api/campaigns/", {
      method: "POST",
      body: JSON.stringify({
        client_name: "Quantum Leap Q4",
        product_desc: "Deep learning infrastructure demand generation",
        budget: 5000,
        audience: "Enterprise architects",
        seed_urls: ["https://theverge.com"],
      }),
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });
  });

  it("posts recon payloads to the recon endpoint", async () => {
    const fetchMock = vi.spyOn(global, "fetch").mockResolvedValue({
      ok: true,
      json: async () => ({ url: "https://wired.com", score: 88 }),
    } as Response);

    await runRecon("https://wired.com", "campaign-123");

    expect(fetchMock).toHaveBeenCalledWith("http://127.0.0.1:8000/api/recon/", {
      method: "POST",
      body: JSON.stringify({
        url: "https://wired.com",
        campaign_id: "campaign-123",
      }),
      headers: {
        "Content-Type": "application/json",
      },
      cache: "no-store",
    });
  });
});
