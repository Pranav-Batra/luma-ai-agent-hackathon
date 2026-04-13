"use client";

import { useEffect, useMemo, useRef, useState } from "react";

import { getCampaignEventsUrl, getGlobalEventsUrl, normalizeEvent } from "@/lib/api";
import type { AgentEvent } from "@/lib/types";

function formatEventTime(timestamp: string) {
  return new Intl.DateTimeFormat("en-US", {
    hour: "numeric",
    minute: "2-digit",
    month: "short",
    day: "numeric",
  }).format(new Date(timestamp));
}

export function LiveFeedPanel({
  campaignId,
  global = false,
  initialEvents,
}: {
  campaignId?: string;
  global?: boolean;
  initialEvents: AgentEvent[];
}) {
  const [events, setEvents] = useState<AgentEvent[]>(initialEvents);
  const [isConnected, setIsConnected] = useState(false);
  const seenIds = useRef(new Set<string>(initialEvents.map((e) => e.id)));

  const streamUrl = global
    ? getGlobalEventsUrl()
    : campaignId
      ? getCampaignEventsUrl(campaignId)
      : null;

  useEffect(() => {
    if (!streamUrl) {
      return;
    }

    const source = new EventSource(streamUrl);

    source.onopen = () => {
      setIsConnected(true);
    };

    source.onmessage = (event) => {
      try {
        const parsed = JSON.parse(event.data) as AgentEvent;
        const normalized = normalizeEvent(parsed);
        if (seenIds.current.has(normalized.id)) return;
        seenIds.current.add(normalized.id);
        setEvents((current) => [normalized, ...current].slice(0, 20));
      } catch {
        // Ignore malformed events from the stream.
      }
    };

    source.onerror = () => {
      setIsConnected(false);
    };

    return () => {
      source.close();
    };
  }, [streamUrl]);

  const headline = useMemo(() => {
    if (isConnected) {
      return global ? "Streaming events across all campaigns" : "SSE stream connected";
    }

    if (streamUrl) {
      return "Listening for live events";
    }

    return "Waiting for an active campaign";
  }, [global, streamUrl, isConnected]);

  return (
    <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
      <div className="flex items-center justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Live optimization feed</p>
          <p className="mt-2 text-sm text-white">{headline}</p>
        </div>
        <span
          className={`rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${
            isConnected
              ? "bg-tertiary/15 text-tertiary ring-1 ring-tertiary/25"
              : "bg-white/6 text-slate-300 ring-1 ring-white/10"
          }`}
        >
          {isConnected ? "Streaming" : "Standby"}
        </span>
      </div>

      <div className="mt-5 space-y-3">
        {events.length > 0 ? (
          events.map((event) => (
            <div key={event.id} className="rounded-[20px] bg-surface-low px-4 py-3 ring-1 ring-white/5">
              <div className="flex flex-wrap items-center justify-between gap-3">
                <p className="text-xs uppercase tracking-[0.18em] text-secondary">
                  {event.event_type.replaceAll("_", " ")}
                </p>
                <p className="text-xs text-slate-400">{formatEventTime(event.created_at)}</p>
              </div>
              <p className="mt-2 text-sm leading-6 text-slate-100">{event.message}</p>
            </div>
          ))
        ) : (
          <div className="rounded-[20px] bg-surface-low px-4 py-5 ring-1 ring-white/5">
            <p className="text-sm text-slate-200">
              {streamUrl
                ? "No agent events yet."
                : "No running campaign selected yet."}
            </p>
            <p className="mt-2 text-sm text-slate-400">
              {streamUrl
                ? "New entries will appear here as soon as the backend records them."
                : "Start or select a campaign to stream live optimization events."}
            </p>
          </div>
        )}
      </div>
    </div>
  );
}
