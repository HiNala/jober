"use client";

import { useMutation, useQuery } from "@tanstack/react-query";
import { Loader2 } from "lucide-react";
import { useState } from "react";
import { toast } from "sonner";

import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { SettingsSection } from "@/components/settings/settings-section";
import {
  createCheckoutSession,
  createPortalSession,
  fetchBillingStatus,
  fetchUsageDashboard,
  isStripeEnabledClient,
} from "@/lib/api/billing";
import { formatApiError } from "@/lib/api/errors";

function siteOrigin() {
  return typeof window !== "undefined" ? window.location.origin : "";
}

export function BillingSettingsSection() {
  const usageQuery = useQuery({ queryKey: ["billing-usage"], queryFn: fetchUsageDashboard });
  const statusQuery = useQuery({
    queryKey: ["billing-status"],
    queryFn: fetchBillingStatus,
    staleTime: 60_000,
    retry: false,
  });
  const [pendingAction, setPendingAction] = useState<"checkout" | "portal" | null>(null);

  const stripeEnabled =
    isStripeEnabledClient() || statusQuery.data?.stripe_enabled === true;
  const plan = statusQuery.data?.plan ?? usageQuery.data?.plan ?? "free";
  const isPro = plan === "pro";
  const hasCustomer = statusQuery.data?.has_stripe_customer === true;
  const usage = usageQuery.data;

  const checkoutMutation = useMutation({
    mutationFn: async () => {
      const origin = siteOrigin();
      return createCheckoutSession({
        successUrl: `${origin}/pricing?checkout=success`,
        cancelUrl: `${origin}/settings`,
      });
    },
    onMutate: () => setPendingAction("checkout"),
    onSuccess: (data) => {
      window.location.href = data.url;
    },
    onError: (err: unknown) => {
      toast.error(formatApiError(err, "Could not start checkout"));
      setPendingAction(null);
    },
  });

  const portalMutation = useMutation({
    mutationFn: async () => {
      return createPortalSession({ returnUrl: `${siteOrigin()}/settings` });
    },
    onMutate: () => setPendingAction("portal"),
    onSuccess: (data) => {
      window.location.href = data.url;
    },
    onError: (err: unknown) => {
      toast.error(formatApiError(err, "Could not open billing portal"));
      setPendingAction(null);
    },
  });

  return (
    <SettingsSection headingId="billing-heading" title="Plan & billing">
      <div className="flex flex-wrap items-center gap-2">
        <p className="text-sm text-muted-foreground">
          Current plan:{" "}
          <Badge variant="secondary" className="align-middle capitalize">
            {plan}
          </Badge>
        </p>
        {statusQuery.data?.subscription_ends_at ? (
          <p className="text-xs text-muted-foreground">
            Period ends {new Date(statusQuery.data.subscription_ends_at).toLocaleDateString()}
          </p>
        ) : null}
      </div>

      {usage ? (
        <div className="mt-4 grid gap-3 sm:grid-cols-3">
          <Card className="border-border/60">
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
          <Card className="border-border/60">
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
          <Card className="border-border/60">
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
      ) : null}

      <div className="mt-4 flex flex-wrap gap-2">
        {stripeEnabled && !isPro ? (
          <Button
            type="button"
            size="sm"
            data-testid="settings-upgrade-pro"
            disabled={pendingAction !== null}
            onClick={() => checkoutMutation.mutate()}
          >
            {pendingAction === "checkout" ? (
              <>
                <Loader2 className="size-4 animate-spin" aria-hidden />
                Starting checkout…
              </>
            ) : (
              "Upgrade to Pro"
            )}
          </Button>
        ) : null}
        {stripeEnabled && (isPro || hasCustomer) ? (
          <Button
            type="button"
            size="sm"
            variant="outline"
            data-testid="settings-manage-billing"
            disabled={pendingAction !== null}
            onClick={() => portalMutation.mutate()}
          >
            {pendingAction === "portal" ? (
              <>
                <Loader2 className="size-4 animate-spin" aria-hidden />
                Opening portal…
              </>
            ) : (
              "Manage billing"
            )}
          </Button>
        ) : null}
        {!stripeEnabled ? (
          <a
            href="/pricing"
            className="inline-flex h-7 items-center rounded-lg border border-border bg-background px-2.5 text-[0.8rem] font-medium hover:bg-muted"
          >
            View pricing & waitlist
          </a>
        ) : null}
      </div>
      {!stripeEnabled ? (
        <p className="mt-2 text-xs text-muted-foreground">
          Self-serve Stripe checkout is not enabled on this environment yet. Join the Pro waitlist
          on the pricing page.
        </p>
      ) : null}
    </SettingsSection>
  );
}
