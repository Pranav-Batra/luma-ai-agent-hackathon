import { Panel, SectionEyebrow, StatusBadge } from "@/components/dashboard/primitives";
import { networkNodes } from "@/lib/dashboard-data";

export default function NetworkMapPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>Network intel</SectionEyebrow>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
          Global distribution of autonomous bidding nodes
        </h1>
        <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
          This specialized intelligence map is currently mock-backed, preserving the Stitch route and
          interaction model until a node topology service exists.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel title="Node overview" description="Latency, load, and regional notes across the mesh">
          <div className="grid gap-4">
            {networkNodes.map((node) => (
              <article
                key={node.id}
                className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-lg font-semibold text-white">{node.id}</p>
                    <p className="mt-1 text-sm text-slate-400">{node.region}</p>
                  </div>
                  <StatusBadge label={node.status} />
                </div>
                <div className="mt-5 grid gap-4 md:grid-cols-3">
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Latency</p>
                    <p className="mt-2 text-lg font-semibold text-white">{node.latency_ms}ms</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Load</p>
                    <p className="mt-2 text-lg font-semibold text-white">{node.bidding_load}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Coordinates</p>
                    <p className="mt-2 text-sm text-slate-300">{node.coordinates}</p>
                  </div>
                </div>
                <p className="mt-4 text-sm leading-6 text-slate-300">{node.note}</p>
              </article>
            ))}
          </div>
        </Panel>

        <Panel title="Live inventory signals" description="Operational notes modeled on the Stitch screen">
          <div className="space-y-4">
            {[
              "04:12:44 // TOKYO High Intent - premium finance inventory detected.",
              "04:11:02 // LONDON Market Volatility - adjusting bid floor to preserve ROAS thresholds.",
              "04:09:15 // SINGAPORE Optimized - all SG core clusters below 5ms internal latency.",
              "04:05:59 // NEW_YORK Standby - maintenance mode with traffic failover engaged.",
            ].map((message) => (
              <div
                key={message}
                className="rounded-[24px] bg-surface-elevated p-5 text-sm leading-6 text-slate-200 ring-1 ring-white/6"
              >
                {message}
              </div>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
