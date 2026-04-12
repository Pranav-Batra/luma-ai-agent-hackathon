import Link from "next/link";

import { LiveFeedPanel } from "@/components/dashboard/live-feed-panel";
import { Panel, SectionEyebrow, StatCard, StatusBadge } from "@/components/dashboard/primitives";
import {
  formatCompact,
  formatCurrency,
  mockCampaigns,
} from "@/lib/dashboard-data";
import { getCampaigns } from "@/lib/api";

export default async function DashboardPage() {
  const campaigns = (await getCampaigns()) ?? mockCampaigns;
  const activeCampaign = campaigns.find((campaign) => campaign.status === "running") ?? campaigns[0];
  const totalSpend = campaigns.reduce((sum, campaign) => sum + campaign.spend, 0);
  const totalImpressions = campaigns.reduce(
    (sum, campaign) => sum + campaign.impressions,
    0,
  );

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-[radial-gradient(circle_at_top_left,rgba(83,221,252,0.16),transparent_28%),linear-gradient(180deg,rgba(15,25,48,0.98),rgba(6,14,32,0.98))] p-8 ring-1 ring-white/8">
        <SectionEyebrow>Global pulse</SectionEyebrow>
        <div className="mt-4 flex flex-wrap items-start justify-between gap-6">
          <div className="max-w-3xl">
            <h1 className="text-4xl font-semibold tracking-tight text-white sm:text-5xl">
              Campaign and recon overview
            </h1>
            <p className="mt-4 text-base leading-7 text-slate-300">
              Track active campaigns, jump into publisher recon, and watch live agent events from
              the current running campaign.
            </p>
          </div>
          <Link
            href="/campaigns/new"
            className="rounded-full bg-white px-5 py-3 text-sm font-semibold text-slate-950"
          >
            Initialize campaign
          </Link>
        </div>

        <div className="mt-8 grid gap-4 md:grid-cols-2 xl:grid-cols-4">
          <StatCard
            label="Active Budget"
            value={formatCurrency(totalSpend || 142500)}
            detail="12% vs last month"
          />
          <StatCard label="Global ROAS" value="4.82x" detail="Autonomous optimized" />
          <StatCard label="System Health" value="99.98%" detail="Real-time synchronization" />
          <StatCard
            label="Impressions"
            value={formatCompact(totalImpressions || 1200000)}
            detail="Across active campaigns"
          />
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[1.1fr_0.9fr]">
        <Panel
          title="Recent campaigns"
          description="Campaign status, spend, and current orchestration state."
          action={
            <Link href="/campaigns" className="text-sm font-medium text-secondary">
              View all
            </Link>
          }
        >
          <div className="overflow-hidden rounded-[24px] bg-surface-low ring-1 ring-white/5">
            <table className="w-full text-left">
              <thead className="bg-black/10 text-xs uppercase tracking-[0.18em] text-slate-400">
                <tr>
                  <th className="px-4 py-3 font-medium">Name & Agent</th>
                  <th className="px-4 py-3 font-medium">Status</th>
                  <th className="px-4 py-3 font-medium">Budget</th>
                  <th className="px-4 py-3 font-medium">Spend</th>
                  <th className="px-4 py-3 font-medium">Impressions</th>
                </tr>
              </thead>
              <tbody>
                {campaigns.map((campaign) => (
                  <tr key={campaign.id} className="border-t border-white/5 text-sm text-slate-200">
                    <td className="px-4 py-4">
                      <Link href={`/campaigns/${campaign.id}`} className="font-medium text-white">
                        {campaign.client_name}
                      </Link>
                      <p className="mt-1 text-xs uppercase tracking-[0.14em] text-slate-500">
                        Agent ARCHITECT-09
                      </p>
                    </td>
                    <td className="px-4 py-4">
                      <StatusBadge label={campaign.status} />
                    </td>
                    <td className="px-4 py-4">{formatCurrency(campaign.budget)}</td>
                    <td className="px-4 py-4">{formatCurrency(campaign.spend)}</td>
                    <td className="px-4 py-4">{formatCompact(campaign.impressions)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </Panel>

        <Panel title="Active agent" description="Current autonomous core load and decision velocity.">
          <div className="space-y-4">
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Processing load</p>
              <p className="mt-3 text-3xl font-semibold text-white">64%</p>
              <p className="mt-2 text-sm text-slate-300">1,242 decisions/sec across live streams.</p>
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Primary campaign</p>
              <p className="mt-3 text-xl font-semibold text-white">
                {activeCampaign?.client_name ?? "Quantum Leap Q4"}
              </p>
              <p className="mt-2 text-sm text-slate-300">
                {activeCampaign?.product_desc ??
                  "Deep learning infrastructure demand generation."}
              </p>
            </div>
          </div>
        </Panel>
      </div>

      <Panel
        title="Live optimization feed"
        description="Agent events across all campaigns stream here in real time."
      >
        <LiveFeedPanel
          key="global-feed"
          global
          initialEvents={[]}
        />
      </Panel>
    </div>
  );
}
