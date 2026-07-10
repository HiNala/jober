"use client";

import { useQuery } from "@tanstack/react-query";
import { Shield, Sparkles } from "lucide-react";

import Link from "next/link";

import { PageHeader } from "@/components/app-shell/page-header";
import { AiSettingsSection } from "@/components/settings/ai-settings-section";
import { AnalyticsConsentSection } from "@/components/settings/analytics-consent-section";
import { AppearanceSettingsSection } from "@/components/settings/appearance-settings-section";
import { ApplicationDefaultsSection } from "@/components/settings/application-defaults-section";
import { AuthSecuritySection } from "@/components/settings/auth-security-section";
import { BillingSettingsSection } from "@/components/settings/billing-settings-section";
import { NotificationsSettingsSection } from "@/components/settings/notifications-settings-section";
import { PrivacyAccountSection } from "@/components/settings/privacy-account-section";
import { SettingsSection } from "@/components/settings/settings-section";
import { PageError, PageLoading } from "@/components/states/page-states";
import { Button, buttonVariants } from "@/components/ui/button";
import { ProfileVault } from "@/components/vault/profile-vault";
import { fetchUsageDashboard } from "@/lib/api/billing";
import { fetchTenantPolicy } from "@/lib/api/settings";
import {
  setWalkthroughDismissed,
  setWalkthroughMarkedComplete,
} from "@/lib/onboarding/first-apply-walkthrough";
import { motionFadeIn, motionPress } from "@/lib/design/motion";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const GUIDANCE_LABELS: Record<string, string> = {
  apply_only_chosen_jobs: "You choose every job",
  respect_site_terms: "Respect site terms",
  no_captcha_bypass: "Human handoff for security",
  sensitive_fields: "Sensitive fields stay manual",
  auto_submit_disclosure: "Auto-submit is opt-in only",
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
    <div className={cn(spacing.page, spacing.section, motionFadeIn)}>
      <PageHeader
        title="Settings"
        description="Vault, billing, application defaults, AI, notifications, and account security — all in one place."
      />

      <section aria-labelledby="vault-settings-heading" className="space-y-3">
        <div className="flex items-center gap-2">
          <Shield className="size-4 text-primary" aria-hidden />
          <h2 id="vault-settings-heading" className="text-sm font-medium">
            Profile & vault
          </h2>
        </div>
        <ProfileVault />
      </section>

      <BillingSettingsSection />
      <SettingsSection headingId="walkthrough-heading" title="First-apply guide">
        <p className="text-sm text-muted-foreground">
          Restart the dashboard checklist that walks you from import → resume → dry-run → review.
        </p>
        <div className="mt-3 flex flex-wrap gap-2">
          <Link
            href="/dashboard"
            className={cn(buttonVariants({ size: "sm" }), motionPress)}
            onClick={() => {
              setWalkthroughDismissed(false);
              setWalkthroughMarkedComplete(false);
            }}
          >
            Open guided walkthrough
          </Link>
          <Button
            type="button"
            size="sm"
            variant="outline"
            onClick={() => {
              setWalkthroughDismissed(false);
              setWalkthroughMarkedComplete(false);
            }}
          >
            Reset checklist progress
          </Button>
        </div>
      </SettingsSection>
      <AppearanceSettingsSection />
      <ApplicationDefaultsSection
        defaultRunPolicy={policy.policy.default_run_policy}
        autoSubmitOptIn={policy.policy.auto_submit_opt_in}
      />
      <AiSettingsSection />
      <NotificationsSettingsSection />
      <AnalyticsConsentSection />
      <AuthSecuritySection />
      <PrivacyAccountSection />

      <p className="text-xs text-muted-foreground">
        Default policy: <span className="capitalize">{defaultPolicy}</span>
        {usage ? (
          <>
            {" "}
            · Batch limit: {usage.limits.max_batch_items} jobs
          </>
        ) : null}
      </p>

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
                key === "auto_submit_disclosure"
                  ? "border-amber-500/35 bg-amber-500/5"
                  : "border-border/60 bg-muted/30",
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
