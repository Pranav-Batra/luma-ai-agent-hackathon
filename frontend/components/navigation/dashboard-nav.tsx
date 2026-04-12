"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

const links = [
  { href: "/", label: "Dashboard" },
  { href: "/campaigns", label: "Campaigns" },
  { href: "/campaigns/new", label: "Create" },
  { href: "/publisher-intelligence", label: "Publisher Recon" },
];

function isActive(pathname: string, href: string) {
  if (href === "/") {
    return pathname === "/";
  }

  return pathname === href || pathname.startsWith(`${href}/`);
}

export function DashboardNav() {
  const pathname = usePathname();

  return (
    <aside className="flex w-full max-w-[280px] flex-col gap-8 rounded-[32px] bg-surface-low px-5 py-6 ring-1 ring-white/6 xl:sticky xl:top-6 xl:h-[calc(100vh-3rem)]">
      <div>
        <p className="text-xs font-semibold uppercase tracking-[0.28em] text-secondary">
          Kinetic Architect
        </p>
        <h1 className="mt-3 text-2xl font-semibold tracking-tight text-white">
          Autonomous Media Console
        </h1>
        <p className="mt-2 text-sm leading-6 text-slate-300">
          Full Stitch dashboard rebuilt on top of the Luma agent backend.
        </p>
      </div>

      <nav className="space-y-2">
        {links.map((link) => {
          const active = isActive(pathname, link.href);

          return (
            <Link
              key={link.href}
              href={link.href}
              className={`flex items-center justify-between rounded-[18px] px-4 py-3 text-sm transition ${
                active
                  ? "bg-[linear-gradient(135deg,rgba(132,85,239,0.28),rgba(186,158,255,0.16))] text-white ring-1 ring-primary/30"
                  : "text-slate-300 hover:bg-white/5 hover:text-white"
              }`}
            >
              <span>{link.label}</span>
              {active ? (
                <span className="h-2 w-2 rounded-full bg-secondary shadow-[0_0_16px_rgba(83,221,252,0.7)]" />
              ) : null}
            </Link>
          );
        })}
      </nav>

      <div className="mt-auto rounded-[24px] bg-surface-elevated p-4 ring-1 ring-white/6">
        <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Agent Pulse</p>
        <div className="mt-3 flex items-center gap-3">
          <span className="relative flex h-3 w-3">
            <span className="absolute inline-flex h-full w-full animate-ping rounded-full bg-secondary/70" />
            <span className="relative inline-flex h-3 w-3 rounded-full bg-secondary" />
          </span>
          <p className="text-sm text-white">Autonomous core scanning active</p>
        </div>
        <p className="mt-3 text-sm text-slate-300">99.9% uptime across live bidding nodes.</p>
      </div>
    </aside>
  );
}
