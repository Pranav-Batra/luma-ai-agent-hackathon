import { CampaignCreateForm } from "@/components/dashboard/campaign-create-form";
import { Panel, SectionEyebrow } from "@/components/dashboard/primitives";

export default function NewCampaignPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>Create new campaign</SectionEyebrow>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
          Initialize an autonomous media stream
        </h1>
        <p className="mt-4 max-w-3xl text-base leading-7 text-slate-300">
          Define your parameters and let the Kinetic engine orchestrate your presence across the
          digital landscape.
        </p>
      </section>

      <Panel
        title="Core identity, targeting, and fiscal power"
        description="Saving will call the campaign create endpoint. Deploy also triggers the campaign run endpoint."
      >
        <CampaignCreateForm />
      </Panel>
    </div>
  );
}
