import Link from "next/link";

import { DashboardNav } from "@/components/navigation/dashboard-nav";

export default function DashboardLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="mx-auto flex min-h-screen w-full max-w-[1600px] flex-col gap-6 px-4 py-4 lg:px-6 xl:flex-row xl:py-6">
      <DashboardNav />
      <div className="min-w-0 flex-1">
        <header className="mb-6 flex flex-wrap items-center justify-between gap-4 rounded-[28px] bg-surface-panel px-6 py-5 ring-1 ring-white/6">
          <div>
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">
              Autonomous media intelligence
            </p>
            <p className="mt-2 text-lg font-semibold text-white">
              Real-time control plane for publisher recon, campaign orchestration, and live agent logs.
            </p>
          </div>
          <div className="flex flex-wrap gap-3">
            <Link
              href="/login"
              className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/5"
            >
              Auth screen
            </Link>
            <Link
              href="/campaigns/new"
              className="rounded-full bg-[linear-gradient(135deg,var(--color-primary-dim),var(--color-primary))] px-4 py-2 text-sm font-semibold text-black"
            >
              Deploy campaign
            </Link>
          </div>
        </header>
        <main>{children}</main>
      </div>
    </div>
  );
}
