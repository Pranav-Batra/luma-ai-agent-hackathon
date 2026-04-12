import { LiveFeedPanel } from "@/components/dashboard/live-feed-panel";
import { Panel, ProgressBar, SectionEyebrow, StatusBadge } from "@/components/dashboard/primitives";
import {
  formatCompact,
  formatCurrency,
  mockCampaigns,
  mockLiveFeed,
} from "@/lib/dashboard-data";
import { getCampaign } from "@/lib/api";

export default async function CampaignDetailPage({
  params,
}: {
  params: Promise<{ id: string }>;
}) {
  const { id } = await params;
  const campaign = (await getCampaign(id)) ?? mockCampaigns.find((item) => item.id === id) ?? mockCampaigns[0];

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>Campaign deep dive & logs</SectionEyebrow>
        <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
          <div className="max-w-4xl">
            <h1 className="text-4xl font-semibold tracking-tight text-white">
              {campaign.client_name}
            </h1>
            <p className="mt-4 text-base leading-7 text-slate-300">{campaign.product_desc}</p>
          </div>
          <StatusBadge label={campaign.status} />
        </div>
      </section>

      <div className="grid gap-6 xl:grid-cols-[0.95fr_1.05fr]">
        <Panel title="Performance envelope" description="Primary KPIs and control toggles">
          <div className="grid gap-4 md:grid-cols-2">
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Total spend</p>
              <p className="mt-3 text-3xl font-semibold text-white">
                {formatCurrency(campaign.spend)}
              </p>
              <p className="mt-2 text-sm text-slate-300">12.4% vs previous month</p>
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Impressions</p>
              <p className="mt-3 text-3xl font-semibold text-white">
                {formatCompact(campaign.impressions)}
              </p>
              <p className="mt-2 text-sm text-slate-300">Multi-channel reach across active inventory</p>
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">ROAS</p>
              <p className="mt-3 text-3xl font-semibold text-white">4.8x</p>
              <p className="mt-2 text-sm text-slate-300">Autonomous optimization remains healthy</p>
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Daily budget allocation</p>
              <p className="mt-3 text-3xl font-semibold text-white">
                {formatCurrency(Math.round(campaign.budget * 0.62))} / {formatCurrency(campaign.budget)}
              </p>
              <div className="mt-3">
                <ProgressBar value={62} />
              </div>
            </div>
          </div>
        </Panel>

        <Panel title="Live event stream" description="Uses SSE when the backend can stream campaign events.">
          <LiveFeedPanel campaignId={campaign.id} initialEvents={mockLiveFeed} />
        </Panel>
      </div>

      <Panel title="Publisher performance" description="A compact cross-publisher performance slice.">
        <div className="overflow-hidden rounded-[24px] bg-surface-low ring-1 ring-white/5">
          <table className="w-full text-left">
            <thead className="bg-black/10 text-xs uppercase tracking-[0.18em] text-slate-400">
              <tr>
                <th className="px-4 py-3 font-medium">Publisher</th>
                <th className="px-4 py-3 font-medium">Impressions</th>
                <th className="px-4 py-3 font-medium">CPC</th>
                <th className="px-4 py-3 font-medium">ROAS</th>
                <th className="px-4 py-3 font-medium">Trend</th>
              </tr>
            </thead>
            <tbody>
              {[
                ["LinkedIn Ads", "1.2M", "$18.40", "5.2x", "Positive"],
                ["Google Search", "3.8M", "$9.12", "4.1x", "Stable"],
                ["Reddit Promoted", "890K", "$4.50", "3.2x", "Learning"],
              ].map((row) => (
                <tr key={row[0]} className="border-t border-white/5 text-sm text-slate-200">
                  {row.map((cell) => (
                    <td key={`${row[0]}-${cell}`} className="px-4 py-4">
                      {cell}
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
