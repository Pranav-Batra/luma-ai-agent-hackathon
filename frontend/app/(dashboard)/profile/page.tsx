import { Panel, SectionEyebrow, StatusBadge } from "@/components/dashboard/primitives";
import { operatorSessions } from "@/lib/dashboard-data";

export default function ProfilePage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>Operator profile</SectionEyebrow>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
          Clearance-level identity and session governance
        </h1>
        <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
          A frontend-first implementation of the Stitch operator profile screen for the control layer.
        </p>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Panel title="Identity" description="Operator record and access posture">
          <div className="rounded-[24px] bg-surface-elevated p-6 ring-1 ring-white/6">
            <StatusBadge label="Encrypted link active" tone="connected" />
            <h2 className="mt-5 text-3xl font-semibold text-white">V. Cooper</h2>
            <p className="mt-2 text-sm text-slate-300">Lead Cyber Intelligence Officer</p>
            <div className="mt-6 grid gap-4 md:grid-cols-2">
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Clearance level</p>
                <p className="mt-2 text-lg font-semibold text-white">Level 4</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Node region</p>
                <p className="mt-2 text-lg font-semibold text-white">North Atlantic 01</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Operator ID</p>
                <p className="mt-2 text-lg font-semibold text-white">#009-X-DELTA</p>
              </div>
              <div>
                <p className="text-xs uppercase tracking-[0.16em] text-slate-500">SSO status</p>
                <p className="mt-2 text-lg font-semibold text-white">Connected</p>
              </div>
            </div>
          </div>
        </Panel>

        <Panel title="Active network sessions" description="Mirrors the device and session grid from Stitch">
          <div className="grid gap-4">
            {operatorSessions.map((session) => (
              <article
                key={`${session.name}-${session.ipAddress}`}
                className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6"
              >
                <div className="flex flex-wrap items-start justify-between gap-4">
                  <div>
                    <p className="text-lg font-semibold text-white">{session.name}</p>
                    <p className="mt-1 text-sm text-slate-400">{session.location}</p>
                  </div>
                  <StatusBadge label={session.status} />
                </div>
                <div className="mt-4 grid gap-4 md:grid-cols-2">
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">IP Address</p>
                    <p className="mt-2 text-sm text-slate-300">{session.ipAddress}</p>
                  </div>
                  <div>
                    <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Last Activity</p>
                    <p className="mt-2 text-sm text-slate-300">{session.lastActivity}</p>
                  </div>
                </div>
              </article>
            ))}
          </div>
        </Panel>
      </div>
    </div>
  );
}
