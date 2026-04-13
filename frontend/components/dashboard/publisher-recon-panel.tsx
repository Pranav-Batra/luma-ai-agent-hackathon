"use client";

import { useState } from "react";

import { runRecon } from "@/lib/api";
import type { Publisher, ReconResult } from "@/lib/types";

function toPublisher(result: ReconResult): Publisher {
  return {
    id: result.url,
    url: result.url,
    contact_email: result.contact_email,
    ad_networks: result.ad_networks,
    estimated_traffic: result.estimated_traffic,
    score: result.score,
    has_adsense: result.has_adsense,
    has_premium_dsp: result.has_premium_dsp,
    trending_headlines: result.trending_headlines,
    created_at: new Date().toISOString(),
  };
}

export function PublisherReconPanel({
  initialPublishers,
}: {
  initialPublishers: Publisher[];
}) {
  const [publishers, setPublishers] = useState(initialPublishers);
  const [url, setUrl] = useState("");
  const [status, setStatus] = useState<string | null>(null);
  const [isRunning, setIsRunning] = useState(false);

  async function handleRecon() {
    if (!url.trim()) {
      return;
    }

    setIsRunning(true);
    setStatus(null);

    const result = await runRecon(url.trim());

    if (!result) {
      setStatus("Recon failed. Check the backend service and try again.");
      setIsRunning(false);
      return;
    }

    setPublishers((current) => [toPublisher(result), ...current]);
    setStatus(`Scanned ${result.url} with score ${result.score}.`);
    setUrl("");
    setIsRunning(false);
  }

  return (
    <div className="space-y-6">
      <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
        <div className="flex flex-col gap-4 lg:flex-row">
          <input
            value={url}
            onChange={(event) => setUrl(event.target.value)}
            className="min-w-0 flex-1 rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-primary/50"
            placeholder="https://venturebeat.com"
          />
          <button
            type="button"
            onClick={handleRecon}
            disabled={isRunning}
            className="rounded-full bg-[linear-gradient(135deg,var(--color-primary-dim),var(--color-primary))] px-5 py-3 text-sm font-semibold text-black transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
          >
            {isRunning ? "Running..." : "Run Intelligence"}
          </button>
        </div>
        {status ? <p className="mt-3 text-sm text-slate-300">{status}</p> : null}
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        {publishers.map((publisher) => (
          <article
            key={`${publisher.id}-${publisher.url}`}
            className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6"
          >
            <div className="flex items-start justify-between gap-4">
              <div>
                <p className="text-sm font-semibold text-white">{publisher.url}</p>
                <p className="mt-1 text-sm text-slate-400">
                  {publisher.contact_email ?? "Contact not found"}
                </p>
              </div>
              <span className="rounded-full bg-secondary/15 px-3 py-1 text-xs font-semibold text-secondary ring-1 ring-secondary/20">
                {publisher.score}%
              </span>
            </div>
            <p className="mt-4 text-sm text-slate-300">
              Traffic: {publisher.estimated_traffic ?? "Unknown"} | Networks:{" "}
              {publisher.ad_networks.join(", ") || "Unclassified"}
            </p>
            {publisher.trending_headlines[0] ? (
              <p className="mt-3 text-sm leading-6 text-slate-200">
                {publisher.trending_headlines[0]}
              </p>
            ) : null}
          </article>
        ))}
      </div>
    </div>
  );
}
