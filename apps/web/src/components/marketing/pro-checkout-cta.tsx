"use client";

import { QueryClient, QueryClientProvider, useMutation, useQuery } from "@tanstack/react-query";
import { ArrowRight, Loader2 } from "lucide-react";
import { useState } from "react";

import { FormError } from "@/components/forms/form-error";
import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { ProWaitlistForm } from "@/components/marketing/pro-waitlist-form";
import { Button } from "@/components/ui/button";
import {
  createCheckoutSession,
  fetchBillingStatus,
  isStripeEnabledClient,
  type BillingStatus,
} from "@/lib/api/billing";
import { ApiError } from "@/lib/api/client";
import { formatApiError } from "@/lib/api/errors";
import { cn } from "@/lib/utils";

function checkoutUrls() {
  const origin = typeof window !== "undefined" ? window.location.origin : "";
  return {
    successUrl: `${origin}/pricing?checkout=success`,
    cancelUrl: `${origin}/pricing?checkout=cancel`,
  };
}

type StatusResult =
  | { kind: "anonymous" }
  | { kind: "authed"; status: BillingStatus };

async function loadBillingAuth(): Promise<StatusResult> {
  try {
    const status = await fetchBillingStatus();
    return { kind: "authed", status };
  } catch (err) {
    if (err instanceof ApiError && err.status === 401) {
      return { kind: "anonymous" };
    }
    // Treat other failures as anonymous for marketing (waitlist/upgrade-after-login).
    return { kind: "anonymous" };
  }
}

/**
 * Pro card CTA on pricing: Stripe Checkout when enabled, else waitlist.
 * Local QueryClient so marketing ShellProviders (no AppProviders) still work.
 */
function ProCheckoutCtaInner({ className }: { className?: string }) {
  const envEnabled = isStripeEnabledClient();
  const [error, setError] = useState<string | null>(null);

  const authQuery = useQuery({
    queryKey: ["billing-status-marketing"],
    queryFn: loadBillingAuth,
    staleTime: 60_000,
    retry: false,
  });

  const checkoutMutation = useMutation({
    mutationFn: async () => createCheckoutSession(checkoutUrls()),
    onSuccess: (data) => {
      window.location.href = data.url;
    },
    onError: (err: unknown) => {
      setError(formatApiError(err, "Could not start checkout. Try again."));
    },
  });

  const stripeEnabled =
    envEnabled ||
    (authQuery.data?.kind === "authed" && authQuery.data.status.stripe_enabled);

  if (authQuery.isLoading && !envEnabled) {
    return (
      <div className={cn("flex justify-center py-2", className)}>
        <Loader2 className="size-5 animate-spin text-muted-foreground" aria-hidden />
        <span className="sr-only">Loading billing…</span>
      </div>
    );
  }

  if (!stripeEnabled) {
    return <ProWaitlistForm className={className} />;
  }

  if (authQuery.isLoading) {
    return (
      <div className={cn("flex justify-center py-2", className)}>
        <Loader2 className="size-5 animate-spin text-muted-foreground" aria-hidden />
        <span className="sr-only">Loading billing…</span>
      </div>
    );
  }

  if (!authQuery.data || authQuery.data.kind === "anonymous") {
    return (
      <div className={cn("space-y-2", className)}>
        <MarketingCtaLink
          href="/signup?next=/pricing"
          feature="pricing_pro_signup"
          size="lg"
          className="w-full"
        >
          Upgrade to Pro
          <ArrowRight className="size-4" aria-hidden />
        </MarketingCtaLink>
        <p className="text-center text-xs text-muted-foreground">
          Already have an account?{" "}
          <a
            href="/login?next=/pricing"
            className="font-medium text-foreground underline-offset-2 hover:underline"
          >
            Sign in
          </a>
        </p>
      </div>
    );
  }

  if (authQuery.data.status.plan === "pro") {
    return (
      <div
        className={cn("rounded-lg border border-primary/30 bg-primary/5 p-4 text-sm", className)}
        role="status"
      >
        <p className="font-medium text-foreground">You are on Pro</p>
        <p className="mt-1 text-muted-foreground">
          Manage billing and invoices from Settings → Plan &amp; billing.
        </p>
        <MarketingCtaLink
          href="/settings"
          feature="pricing_pro_settings"
          size="lg"
          className="mt-4 w-full"
          variant="outline"
        >
          Open settings
        </MarketingCtaLink>
      </div>
    );
  }

  return (
    <div className={cn("space-y-2", className)}>
      {error ? <FormError message={error} /> : null}
      <Button
        type="button"
        size="lg"
        className="w-full"
        data-testid="pricing-upgrade-pro"
        disabled={checkoutMutation.isPending}
        onClick={() => {
          setError(null);
          checkoutMutation.mutate();
        }}
      >
        {checkoutMutation.isPending ? (
          <>
            <Loader2 className="size-4 animate-spin" aria-hidden />
            Redirecting to Stripe…
          </>
        ) : (
          <>
            Upgrade to Pro
            <ArrowRight className="size-4" aria-hidden />
          </>
        )}
      </Button>
      <p className="text-center text-xs text-muted-foreground">
        Secure checkout via Stripe · cancel anytime
      </p>
    </div>
  );
}

export function ProCheckoutCta({ className }: { className?: string }) {
  const [client] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: { retry: false, refetchOnWindowFocus: false },
        },
      }),
  );

  return (
    <QueryClientProvider client={client}>
      <ProCheckoutCtaInner className={className} />
    </QueryClientProvider>
  );
}
