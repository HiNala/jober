"use client";

import Link from "next/link";
import { ArrowRight, Clock } from "lucide-react";
import { useEffect, useState } from "react";

import { useUserPreferences } from "@/contexts/user-preferences-context";
import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { fetchDashboardSummary, type DashboardSummary } from "@/lib/api/batches";

import { buttonVariants } from "@/components/ui/button";

export function NeedsAttentionBanner() {
  const { preferences } = useUserPreferences();
  const [summary, setSummary] = useState<DashboardSummary | null>(null);

  useEffect(() => {
    let cancelled = false;
    const load = async () => {
      try {
        const data = await fetchDashboardSummary();
        if (!cancelled) setSummary(data);
      } catch {
        if (!cancelled) setSummary(null);
      }
    };
    void load();
    const timer = setInterval(() => void load(), 8000);
    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, []);

  const needsReview = summary?.needs_review ?? 0;
  const activeRuns = summary?.active_runs ?? 0;

  if (!preferences?.notifications.in_app_run_attention) {
    return null;
  }

  if (!summary || (needsReview === 0 && activeRuns === 0)) {
    return null;
  }

  const primary =
    needsReview > 0
      ? {
          headline: `${needsReview} run${needsReview === 1 ? "" : "s"} need your review`,
          detail: "Open a checkpoint to approve, edit, or hand off before submit.",
          href: "/queue",
          cta: "Review queue",
        }
      : {
          headline: `${activeRuns} active run${activeRuns === 1 ? "" : "s"} in progress`,
          detail: "Runs stream live in the console — nothing to approve yet.",
          href: "/dashboard",
          cta: "Watch events",
        };

  return (
    <section
      className={cn(
        "flex flex-col gap-3 rounded-lg border border-primary/25 bg-primary/5 p-4 sm:flex-row sm:items-center sm:justify-between",
        motionFadeIn,
      )}
      aria-label="What needs you now"
    >
      <div className="flex gap-3">
        <Clock className="mt-0.5 size-5 shrink-0 text-primary" aria-hidden />
        <div>
          <h2 className="text-sm font-semibold">{primary.headline}</h2>
          <p className="mt-0.5 text-sm text-muted-foreground">{primary.detail}</p>
        </div>
      </div>
      <Link
        href={primary.href}
        className={cn(buttonVariants({ size: "sm", variant: "secondary" }), "shrink-0 inline-flex gap-1")}
      >
        {primary.cta}
        <ArrowRight className="size-4" aria-hidden />
      </Link>
    </section>
  );
}
