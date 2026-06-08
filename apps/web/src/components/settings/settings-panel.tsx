"use client";

import { useQuery } from "@tanstack/react-query";
import { Shield, Sparkles } from "lucide-react";

import { AiSettingsSection } from "@/components/settings/ai-settings-section";
import { AppearanceSettingsSection } from "@/components/settings/appearance-settings-section";
import { ApplicationDefaultsSection } from "@/components/settings/application-defaults-section";
import { AuthSecuritySection } from "@/components/settings/auth-security-section";
import { NotificationsSettingsSection } from "@/components/settings/notifications-settings-section";
import { PrivacyAccountSection } from "@/components/settings/privacy-account-section";
import { PageError, PageLoading } from "@/components/states/page-states";
import { ProfileVault } from "@/components/vault/profile-vault";
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

function SettingsPanelInner() {
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
        message="Could not load plan and policy. Ensure the API is running and you are signed in."
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
          Profile vault, application behavior, AI, appearance, and account security.
        </p>
      </header>

      <section aria-labelledby="vault-settings-heading" className="space-y-3">
        <div className="flex items-center gap-2">
          <Shield className="size-4 text-primary" aria-hidden />
          <h2 id="vault-settings-heading" className="text-sm font-medium">
            Profile & vault
          </h2>
        </div>
        <ProfileVault />
      </section>

      <AppearanceSettingsSection />
      <ApplicationDefaultsSection
        defaultRunPolicy={policy.policy.default_run_policy}
        autoSubmitOptIn={policy.policy.auto_submit_opt_in}
      />
      <AiSettingsSection />
      <NotificationsSettingsSection />
      <AuthSecuritySection />
      <PrivacyAccountSection />

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
          {usage.limits.max_batch_items} jobs · Default policy:{" "}
          <span className="capitalize">{defaultPolicy}</span>
        </p>
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

export function SettingsPanel() {
  return <SettingsPanelInner />;
}
