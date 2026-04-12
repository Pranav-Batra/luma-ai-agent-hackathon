import { PublisherReconPanel } from "@/components/dashboard/publisher-recon-panel";
import { Panel, SectionEyebrow } from "@/components/dashboard/primitives";
import { mockPublishers } from "@/lib/dashboard-data";
import { getPublishers } from "@/lib/api";

export default async function PublisherIntelligencePage() {
  const publishers = (await getPublishers(70)) ?? mockPublishers;

  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>Publisher reconnaissance</SectionEyebrow>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
          Autonomous crawler analyzing domain quality and ad-inventory density
        </h1>
        <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
          This route is partially real-data backed today through the publishers and recon API endpoints.
        </p>
      </section>

      <Panel
        title="Recon control plane"
        description="Run live recon against any publisher URL, or browse the highest-scoring publishers already discovered."
      >
        <PublisherReconPanel initialPublishers={publishers} />
      </Panel>
    </div>
  );
}
