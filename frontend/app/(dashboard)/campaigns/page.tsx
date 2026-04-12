import Link from "next/link";

import { Panel, SectionEyebrow, StatusBadge } from "@/components/dashboard/primitives";
import { formatCompact, formatCurrency, mockCampaigns } from "@/lib/dashboard-data";
import { getCampaigns } from "@/lib/api";

export default async function CampaignsPage() {
  const campaigns = (await getCampaigns()) ?? mockCampaigns;

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>Campaign management</SectionEyebrow>
        <div className="mt-4 flex flex-wrap items-start justify-between gap-4">
          <div>
            <h1 className="text-4xl font-semibold tracking-tight text-white">
              Campaign control plane
            </h1>
            <p className="mt-3 max-w-3xl text-base leading-7 text-slate-300">
              Review campaign status, spend, and audience details from the backend campaign API.
            </p>
          </div>
          <Link
            href="/campaigns/new"
            className="rounded-full bg-[linear-gradient(135deg,var(--color-primary-dim),var(--color-primary))] px-5 py-3 text-sm font-semibold text-black"
          >
            Create new campaign
          </Link>
        </div>
      </section>

      <Panel
        title="Campaign roster"
        description={`Showing ${campaigns.length} campaign records from the campaign service or local fallback data.`}
      >
        <div className="grid gap-4">
          {campaigns.map((campaign) => (
            <article
              key={campaign.id}
              className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6"
            >
              <div className="flex flex-wrap items-start justify-between gap-4">
                <div>
                  <Link
                    href={`/campaigns/${campaign.id}`}
                    className="text-xl font-semibold text-white"
                  >
                    {campaign.client_name}
                  </Link>
                  <p className="mt-2 max-w-3xl text-sm leading-6 text-slate-300">
                    {campaign.product_desc}
                  </p>
                </div>
                <StatusBadge label={campaign.status} />
              </div>

              <div className="mt-5 grid gap-4 md:grid-cols-4">
                <div>
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Budget</p>
                  <p className="mt-2 text-lg font-semibold text-white">
                    {formatCurrency(campaign.budget)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Spend</p>
                  <p className="mt-2 text-lg font-semibold text-white">
                    {formatCurrency(campaign.spend)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Impressions</p>
                  <p className="mt-2 text-lg font-semibold text-white">
                    {formatCompact(campaign.impressions)}
                  </p>
                </div>
                <div>
                  <p className="text-xs uppercase tracking-[0.16em] text-slate-500">Audience</p>
                  <p className="mt-2 text-sm text-slate-300">{campaign.audience}</p>
                </div>
              </div>
            </article>
          ))}
        </div>
      </Panel>
    </div>
  );
}
