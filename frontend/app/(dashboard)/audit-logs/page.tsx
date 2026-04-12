import { Panel, SectionEyebrow, StatusBadge } from "@/components/dashboard/primitives";
import { auditLogItems } from "@/lib/dashboard-data";

export default function AuditLogsPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>System logs</SectionEyebrow>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
          Immutable ledger of autonomous operations and agent re-prioritizations
        </h1>
        <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
          The webhook route already emits reply events into the backend agent event stream. This
          richer audit surface remains mock-backed until a dedicated log listing endpoint exists.
        </p>
      </section>

      <Panel title="Audit trail" description="Modeled after the Stitch system logs screen">
        <div className="overflow-hidden rounded-[24px] bg-surface-low ring-1 ring-white/5">
          <table className="w-full text-left">
            <thead className="bg-black/10 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Timestamp</th>
                <th className="px-4 py-3 font-medium">Agent ID</th>
                <th className="px-4 py-3 font-medium">Action Type</th>
                <th className="px-4 py-3 font-medium">Status</th>
                <th className="px-4 py-3 font-medium">Data Hash</th>
                <th className="px-4 py-3 font-medium">Raw</th>
              </tr>
            </thead>
            <tbody>
              {auditLogItems.map((item) => (
                <tr key={item.id} className="border-t border-white/5 text-sm text-slate-200">
                  <td className="px-4 py-4">{item.timestamp}</td>
                  <td className="px-4 py-4">{item.agent_id}</td>
                  <td className="px-4 py-4">{item.action_type}</td>
                  <td className="px-4 py-4">
                    <StatusBadge label={item.status} />
                  </td>
                  <td className="px-4 py-4 font-mono text-xs text-slate-300">{item.data_hash}</td>
                  <td className="px-4 py-4">{item.raw}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </Panel>

      <Panel title="Live agent stream" description="Representative system console messages">
        <div className="space-y-3 font-mono text-sm">
          {[
            "[14:22:04] INFO: Agent BID_UNIT_09 identified arbitrage opportunity in US-EAST-1.",
            "[14:22:05] INFO: Calculating risk parameters with confidence interval 0.94.",
            "[14:22:06] ACTION: Executing LOCK_BID command on hash 0x7f4a...9b12.",
            "[14:22:10] INFO: Success. Transaction committed.",
          ].map((line) => (
            <div key={line} className="rounded-[20px] bg-surface-elevated px-4 py-3 text-slate-200 ring-1 ring-white/6">
              {line}
            </div>
          ))}
        </div>
      </Panel>
    </div>
  );
}
