import { Panel, SectionEyebrow, StatusBadge } from "@/components/dashboard/primitives";
import { analyticsActions, analyticsTimeline, topLeaders } from "@/lib/dashboard-data";

export default function AnalyticsPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>System analytics</SectionEyebrow>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
          Deep-stream retrospective analysis of autonomous media buying agents
        </h1>
        <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
          This screen mirrors the Stitch analytics dashboard with mock rollups until dedicated
          aggregation endpoints exist.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.05fr_0.95fr]">
        <Panel title="30-day performance correlation" description="Daily spend versus dynamic ROAS">
          <div className="grid gap-4 md:grid-cols-4">
            {analyticsTimeline.map((point) => (
              <div key={point.label} className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
                <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{point.label}</p>
                <p className="mt-3 text-2xl font-semibold text-white">${point.spend}</p>
                <p className="mt-2 text-sm text-slate-300">{point.roas.toFixed(1)}x ROAS</p>
              </div>
            ))}
          </div>
        </Panel>

        <Panel title="Autonomous task automation index" description="Execution confidence and human override share">
          <div className="grid gap-4 md:grid-cols-3">
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Autonomous</p>
              <p className="mt-3 text-3xl font-semibold text-white">94%</p>
              <StatusBadge label="Active" tone="live" />
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Manual intervention</p>
              <p className="mt-3 text-3xl font-semibold text-white">1.2%</p>
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Saved hours</p>
              <p className="mt-3 text-3xl font-semibold text-white">2,480</p>
            </div>
          </div>
        </Panel>
      </div>

      <Panel title="Performance leaders" description="Volume and conversion leaders across the network">
        <div className="grid gap-4 lg:grid-cols-2">
          {topLeaders.map((leader) => (
            <article
              key={leader.name}
              className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6"
            >
              <p className="text-sm font-semibold text-white">{leader.name}</p>
              <p className="mt-2 text-3xl font-semibold text-secondary">{leader.conversions}</p>
              <p className="mt-2 text-sm text-slate-300">{leader.note}</p>
            </article>
          ))}
        </div>
      </Panel>

      <Panel title="Action log" description="Recent automated optimization decisions">
        <div className="overflow-hidden rounded-[24px] bg-surface-low ring-1 ring-white/5">
          <table className="w-full text-left">
            <thead className="bg-black/10 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">Agent</th>
                <th className="px-4 py-3 font-medium">Action</th>
                <th className="px-4 py-3 font-medium">Target CPM</th>
                <th className="px-4 py-3 font-medium">Outcome ROAS</th>
                <th className="px-4 py-3 font-medium">Status</th>
              </tr>
            </thead>
            <tbody>
              {analyticsActions.map((row) => (
                <tr key={row.join("-")} className="border-t border-white/5 text-sm text-slate-200">
                  {row.map((cell, index) => (
                    <td key={`${row[0]}-${index}`} className="px-4 py-4">
                      {index === 5 ? <StatusBadge label={cell} /> : cell}
                    </td>
                  ))}
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>
    </div>
  );
}
