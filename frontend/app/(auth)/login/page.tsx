import Link from "next/link";

export default function LoginPage() {
  return (
    <main className="mx-auto flex min-h-screen w-full max-w-7xl items-center px-6 py-10 lg:px-10">
      <div className="grid w-full gap-6 lg:grid-cols-[1.1fr_0.9fr]">
        <section className="rounded-[36px] bg-[radial-gradient(circle_at_top_left,rgba(83,221,252,0.18),transparent_28%),linear-gradient(180deg,rgba(15,25,48,0.98),rgba(6,14,32,0.98))] p-8 ring-1 ring-white/8">
          <p className="text-xs font-semibold uppercase tracking-[0.28em] text-secondary">
            Kinetic Architect
          </p>
          <h1 className="mt-6 max-w-xl text-5xl font-semibold tracking-tight text-white">
            Control the autonomous flow.
          </h1>
          <p className="mt-5 max-w-2xl text-lg leading-8 text-slate-300">
            Real-time media intelligence powered by high-frequency agent architecture.
            Secure access to your bidding ecosystem.
          </p>

          <div className="mt-10 grid gap-4 sm:grid-cols-3">
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Latency floor</p>
              <p className="mt-3 text-3xl font-semibold text-white">2.4ms</p>
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Agent uptime</p>
              <p className="mt-3 text-3xl font-semibold text-white">99.9%</p>
            </div>
            <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
              <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Signals daily</p>
              <p className="mt-3 text-3xl font-semibold text-white">14.2B</p>
            </div>
          </div>

          <p className="mt-8 text-sm text-slate-400">
            Autonomous Core v2.4 network scanning active. System Node: US-EAST-1. ISO 27001 compliant.
          </p>
        </section>

        <section className="rounded-[36px] bg-surface-panel p-8 ring-1 ring-white/8">
          <p className="text-xs font-semibold uppercase tracking-[0.22em] text-slate-400">
            Authenticate
          </p>
          <div className="mt-6 space-y-4">
            <div>
              <label className="text-sm text-slate-300">Work Email</label>
              <input
                className="mt-2 w-full rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                placeholder="operator@luma.ai"
              />
            </div>
            <div>
              <div className="flex items-center justify-between gap-3">
                <label className="text-sm text-slate-300">Password</label>
                <span className="text-sm text-secondary">Forgot?</span>
              </div>
              <input
                type="password"
                className="mt-2 w-full rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500"
                placeholder="••••••••••"
              />
            </div>
          </div>

          <Link
            href="/"
            className="mt-8 flex items-center justify-center rounded-full bg-[linear-gradient(135deg,var(--color-primary-dim),var(--color-primary))] px-5 py-3 text-sm font-semibold text-black"
          >
            Authenticate
          </Link>

          <div className="mt-8 rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
            <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Continue with</p>
            <div className="mt-4 flex flex-wrap gap-3">
              {["Biometrics", "Passkey", "SSO Login"].map((item) => (
                <button
                  key={item}
                  type="button"
                  className="rounded-full border border-white/10 px-4 py-2 text-sm text-slate-200 transition hover:bg-white/5"
                >
                  {item}
                </button>
              ))}
            </div>
          </div>
        </section>
      </div>
    </main>
  );
}
