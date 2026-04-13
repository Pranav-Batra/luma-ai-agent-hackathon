import type { ReactNode } from "react";

import { getStatusTone } from "@/lib/dashboard-data";

function badgeClasses(tone: string) {
  switch (tone) {
    case "live":
      return "bg-secondary/15 text-secondary ring-1 ring-secondary/30";
    case "warning":
      return "bg-yellow-300/10 text-yellow-200 ring-1 ring-yellow-300/20";
    case "danger":
      return "bg-red-400/10 text-red-200 ring-1 ring-red-400/20";
    case "connected":
      return "bg-tertiary/15 text-tertiary ring-1 ring-tertiary/30";
    default:
      return "bg-white/6 text-slate-200 ring-1 ring-white/10";
  }
}

export function StatusBadge({
  label,
  tone,
}: {
  label: string;
  tone?: string;
}) {
  const resolvedTone = tone ?? getStatusTone(label);

  return (
    <span
      className={`inline-flex items-center rounded-full px-3 py-1 text-xs font-semibold uppercase tracking-[0.18em] ${badgeClasses(
        resolvedTone,
      )}`}
    >
      {label}
    </span>
  );
}

export function Panel({
  title,
  description,
  action,
  children,
  className = "",
}: {
  title: string;
  description?: string;
  action?: ReactNode;
  children: ReactNode;
  className?: string;
}) {
  return (
    <section
      className={`rounded-[28px] bg-surface-panel p-6 shadow-[0_20px_80px_rgba(8,15,38,0.35)] ring-1 ring-white/6 ${className}`}
    >
      <div className="flex flex-wrap items-start justify-between gap-4">
        <div className="space-y-2">
          <h2 className="text-xl font-semibold tracking-tight text-white">{title}</h2>
          {description ? (
            <p className="max-w-2xl text-sm leading-6 text-slate-300">{description}</p>
          ) : null}
        </div>
        {action ? <div>{action}</div> : null}
      </div>
      <div className="mt-6">{children}</div>
    </section>
  );
}

export function StatCard({
  label,
  value,
  detail,
}: {
  label: string;
  value: string;
  detail: string;
}) {
  return (
    <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
      <p className="text-xs uppercase tracking-[0.18em] text-slate-400">{label}</p>
      <p className="mt-4 text-3xl font-semibold tracking-tight text-white">{value}</p>
      <p className="mt-2 text-sm text-slate-300">{detail}</p>
    </div>
  );
}

export function SurfaceList({
  items,
}: {
  items: Array<{ label: string; value: string; detail?: string }>;
}) {
  return (
    <div className="space-y-3">
      {items.map((item) => (
        <div
          key={`${item.label}-${item.value}`}
          className="rounded-[20px] bg-surface-low px-4 py-3 ring-1 ring-white/5"
        >
          <div className="flex items-center justify-between gap-4">
            <p className="text-sm text-slate-300">{item.label}</p>
            <p className="text-sm font-medium text-white">{item.value}</p>
          </div>
          {item.detail ? <p className="mt-2 text-xs text-slate-400">{item.detail}</p> : null}
        </div>
      ))}
    </div>
  );
}

export function SectionEyebrow({ children }: { children: ReactNode }) {
  return (
    <p className="text-xs font-semibold uppercase tracking-[0.24em] text-secondary">
      {children}
    </p>
  );
}

export function ProgressBar({ value }: { value: number }) {
  return (
    <div className="h-2 overflow-hidden rounded-full bg-white/6">
      <div
        className="h-full rounded-full bg-[linear-gradient(90deg,var(--color-primary-dim),var(--color-primary))]"
        style={{ width: `${Math.max(0, Math.min(100, value))}%` }}
      />
    </div>
  );
}
