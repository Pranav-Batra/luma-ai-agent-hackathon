import { Panel, SectionEyebrow, StatusBadge } from "@/components/dashboard/primitives";
import { settingSections } from "@/lib/dashboard-data";

export default function SettingsPage() {
  return (
    <div className="space-y-6">
      <section className="rounded-[32px] bg-surface-panel p-8 ring-1 ring-white/6">
        <SectionEyebrow>Agent settings</SectionEyebrow>
        <h1 className="mt-4 text-4xl font-semibold tracking-tight text-white">
          Configure core autonomous logic and strategic integrations
        </h1>
        <p className="mt-4 max-w-4xl text-base leading-7 text-slate-300">
          These controls are currently UI-first and mirror the Stitch design while backend-backed
          persistence is still pending.
        </p>
      </section>

      <div className="grid gap-6">
        {settingSections.map((section) => (
          <Panel
            key={section.title}
            title={section.title}
            description={section.description}
          >
            <div className="grid gap-4 md:grid-cols-3">
              {section.items.map((item) => (
                <article
                  key={`${section.title}-${item.label}`}
                  className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6"
                >
                  <div className="flex items-start justify-between gap-3">
                    <p className="text-sm font-semibold text-white">{item.label}</p>
                    {item.status ? <StatusBadge label={item.status} tone={item.status} /> : null}
                  </div>
                  <p className="mt-3 text-lg font-semibold text-secondary">{item.value}</p>
                  <p className="mt-3 text-sm leading-6 text-slate-300">{item.hint}</p>
                </article>
              ))}
            </div>
          </Panel>
        ))}
      </div>
    </div>
  );
}
