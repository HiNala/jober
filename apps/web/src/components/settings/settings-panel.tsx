"use client";

import { useQuery } from "@tanstack/react-query";
import { Shield, Sparkles } from "lucide-react";

import { AuthSecuritySection } from "@/components/settings/auth-security-section";
import { PageError, PageLoading } from "@/components/states/page-states";
import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { fetchUsageDashboard } from "@/lib/api/billing";
import { fetchTenantPolicy } from "@/lib/api/settings";
import { motionFadeIn } from "@/lib/design/motion";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const GUIDANCE_LABELS: Record<string, string> = {
  apply_only_chosen_jobs: "You choose every job",
  respect_site_terms: "Respect site terms",
  no_captcha_bypass: "Human handoff for security",
  sensitive_fields: "Sensitive fields",
  auto_submit_disclosure: "auto_submit disclosure",
};

export function SettingsPanel() {
  const policyQuery = useQuery({
    queryKey: ["tenant-policy"],
    queryFn: fetchTenantPolicy,
  });
  const usageQuery = useQuery({
    queryKey: ["billing-usage"],
    queryFn: fetchUsageDashboard,
  });

  if (policyQuery.isLoading || usageQuery.isLoading) {
    return <PageLoading label="Loading settings…" />;
  }

  if (policyQuery.isError || usageQuery.isError || !policyQuery.data || !usageQuery.data) {
    return (
      <PageError
        title="Settings unavailable"
        message="Could not load plan and policy. Ensure the API is running and auth headers are set."
        onRetry={() => {
          void policyQuery.refetch();
          void usageQuery.refetch();
        }}
      />
    );
  }

  const policy = policyQuery.data;
  const usage = usageQuery.data;
  const defaultPolicy = policy.policy.default_run_policy.replace(/_/g, " ");

  return (
    <div className={cn(spacing.section, motionFadeIn)}>
      <header>
        <h1 className="text-lg font-semibold tracking-tight">Settings</h1>
        <p className="mt-1 text-sm text-muted-foreground">
          Plan limits, run policy defaults, and responsible-use guidance.
        </p>
      </header>

      <AuthSecuritySection />

      <section aria-labelledby="usage-heading">
        <h2 id="usage-heading" className="mb-3 text-sm font-medium">
          Usage this month
        </h2>
        <div className="grid gap-4 sm:grid-cols-3">
          <Card className={surface.card}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Application runs
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-semibold tabular-nums">
                {usage.usage.monthly_runs}
                <span className="text-sm font-normal text-muted-foreground">
                  {" "}
                  / {usage.limits.max_monthly_runs}
                </span>
              </p>
            </CardContent>
          </Card>
          <Card className={surface.card}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                Documents
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-semibold tabular-nums">
                {usage.usage.documents_generated}
              </p>
            </CardContent>
          </Card>
          <Card className={surface.card}>
            <CardHeader className="pb-2">
              <CardTitle className="text-sm font-medium text-muted-foreground">
                LLM spend
              </CardTitle>
            </CardHeader>
            <CardContent>
              <p className="text-2xl font-semibold tabular-nums">
                ${usage.usage.llm_cost_usd.toFixed(2)}
                <span className="text-sm font-normal text-muted-foreground">
                  {" "}
                  / ${usage.limits.max_llm_budget_usd.toFixed(0)}
                </span>
              </p>
            </CardContent>
          </Card>
        </div>
        <p className="mt-2 text-xs text-muted-foreground">
          Plan: <Badge variant="secondary">{usage.plan}</Badge> · Batch limit:{" "}
          {usage.limits.max_batch_items} jobs
        </p>
      </section>

      <section aria-labelledby="policy-heading" className={cn(surface.card, "rounded-lg p-4")}>
        <div className="mb-3 flex items-center gap-2">
          <Shield className="size-4 text-primary" aria-hidden />
          <h2 id="policy-heading" className="text-sm font-medium">
            Run policy defaults
          </h2>
        </div>
        <dl className="grid gap-2 text-sm sm:grid-cols-2">
          <div>
            <dt className="text-muted-foreground">Default policy</dt>
            <dd className="font-medium capitalize">{defaultPolicy}</dd>
          </div>
          <div>
            <dt className="text-muted-foreground">auto_submit opt-in</dt>
            <dd className="font-medium">
              {policy.policy.auto_submit_opt_in ? "Enabled" : "Off (recommended)"}
            </dd>
          </div>
          <div>
            <dt className="text-muted-foreground">Data retention</dt>
            <dd className="font-medium">
              {policy.policy.retention_days
                ? `${policy.policy.retention_days} days`
                : "Account default"}
            </dd>
          </div>
        </dl>
      </section>

      <section aria-labelledby="guidance-heading">
        <div className="mb-3 flex items-center gap-2">
          <Sparkles className="size-4 text-accent" aria-hidden />
          <h2 id="guidance-heading" className="text-sm font-medium">
            Responsible use
          </h2>
        </div>
        <ul className="space-y-3">
          {Object.entries(policy.usage_guidance).map(([key, body]) => (
            <li
              key={key}
              className={cn(
                "rounded-lg border p-3 text-sm",
                key === "auto_submit_disclosure" && "border-amber-500/35 bg-amber-500/5",
              )}
            >
              <p className="font-medium">{GUIDANCE_LABELS[key] ?? key}</p>
              <p className="mt-1 text-muted-foreground">{body}</p>
            </li>
          ))}
        </ul>
      </section>
    </div>
  );
}
