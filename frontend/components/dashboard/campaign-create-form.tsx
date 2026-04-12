"use client";

import { useState } from "react";
import { useRouter } from "next/navigation";

import { createCampaign, runCampaign } from "@/lib/api";

const initialState = {
  client_name: "",
  product_desc: "",
  budget: 5000,
  audience: "",
  seed_urls: "",
};

export function CampaignCreateForm() {
  const router = useRouter();
  const [formState, setFormState] = useState(initialState);
  const [isSubmitting, setIsSubmitting] = useState(false);
  const [error, setError] = useState<string | null>(null);

  async function handleSubmit(mode: "draft" | "deploy") {
    setIsSubmitting(true);
    setError(null);

    const payload = {
      client_name: formState.client_name,
      product_desc: formState.product_desc,
      budget: Number(formState.budget),
      audience: formState.audience,
      seed_urls: formState.seed_urls
        .split("\n")
        .map((value) => value.trim())
        .filter(Boolean),
    };

    const campaign = await createCampaign(payload);

    if (!campaign) {
      setError("Could not create the campaign. Verify the FastAPI backend is running.");
      setIsSubmitting(false);
      return;
    }

    if (mode === "deploy") {
      await runCampaign(campaign.id);
    }

    router.push(`/campaigns/${campaign.id}`);
    router.refresh();
  }

  return (
    <div className="grid gap-6 lg:grid-cols-[1.3fr_0.7fr]">
      <div className="space-y-5">
        <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
          <label htmlFor="client_name" className="block text-sm font-medium text-slate-200">
            Client Name
          </label>
          <input
            id="client_name"
            value={formState.client_name}
            onChange={(event) =>
              setFormState((current) => ({ ...current, client_name: event.target.value }))
            }
            className="mt-3 w-full rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-primary/50"
            placeholder="Quantum Leap Q4"
          />
        </div>

        <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
          <label htmlFor="product_desc" className="block text-sm font-medium text-slate-200">
            Product Description
          </label>
          <textarea
            id="product_desc"
            value={formState.product_desc}
            onChange={(event) =>
              setFormState((current) => ({ ...current, product_desc: event.target.value }))
            }
            className="mt-3 min-h-32 w-full rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-primary/50"
            placeholder="Describe the offer, product motion, and creative intent."
          />
        </div>

        <div className="grid gap-5 md:grid-cols-2">
          <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
            <label htmlFor="audience" className="block text-sm font-medium text-slate-200">
              Target Audience Keywords
            </label>
            <textarea
              id="audience"
              value={formState.audience}
              onChange={(event) =>
                setFormState((current) => ({ ...current, audience: event.target.value }))
              }
              className="mt-3 min-h-28 w-full rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-primary/50"
              placeholder="Enterprise architects, CTOs, cloud platform teams"
            />
          </div>

          <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
            <label htmlFor="budget" className="block text-sm font-medium text-slate-200">
              Budget (USD)
            </label>
            <input
              id="budget"
              type="number"
              min={500}
              value={formState.budget}
              onChange={(event) =>
                setFormState((current) => ({
                  ...current,
                  budget: Number(event.target.value),
                }))
              }
              className="mt-3 w-full rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-primary/50"
            />
            <p className="mt-3 text-sm text-slate-400">
              Recommended: $5,000+ for stronger training and optimization windows.
            </p>
          </div>
        </div>

        <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
          <label htmlFor="seed_urls" className="block text-sm font-medium text-slate-200">
            Seed URLs (one per line)
          </label>
          <textarea
            id="seed_urls"
            value={formState.seed_urls}
            onChange={(event) =>
              setFormState((current) => ({ ...current, seed_urls: event.target.value }))
            }
            className="mt-3 min-h-36 w-full rounded-[18px] border border-white/10 bg-surface-low px-4 py-3 text-sm text-white outline-none placeholder:text-slate-500 focus:border-primary/50"
            placeholder={"https://theverge.com\nhttps://wired.com"}
          />
        </div>

        {error ? (
          <div className="rounded-[20px] bg-red-400/10 px-4 py-3 text-sm text-red-200 ring-1 ring-red-400/20">
            {error}
          </div>
        ) : null}
      </div>

      <div className="space-y-5">
        <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
          <p className="text-xs uppercase tracking-[0.18em] text-slate-400">Autonomous ensemble</p>
          <p className="mt-3 text-2xl font-semibold text-white">5 agents initialized</p>
          <p className="mt-3 text-sm leading-6 text-slate-300">
            Create will persist the campaign through FastAPI. Deploy will immediately trigger the run endpoint.
          </p>
        </div>

        <div className="rounded-[24px] bg-surface-elevated p-5 ring-1 ring-white/6">
          <div className="flex flex-col gap-3">
            <button
              type="button"
              disabled={isSubmitting}
              onClick={() => handleSubmit("draft")}
              className="rounded-full bg-white px-4 py-3 text-sm font-semibold text-slate-950 transition hover:bg-slate-100 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? "Saving..." : "Save Draft"}
            </button>
            <button
              type="button"
              disabled={isSubmitting}
              onClick={() => handleSubmit("deploy")}
              className="rounded-full bg-[linear-gradient(135deg,var(--color-primary-dim),var(--color-primary))] px-4 py-3 text-sm font-semibold text-black transition hover:opacity-95 disabled:cursor-not-allowed disabled:opacity-60"
            >
              {isSubmitting ? "Deploying..." : "Deploy Campaign"}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}
