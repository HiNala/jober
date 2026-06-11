"use client";

import { PageError } from "@/components/states/page-states";
import { friendlyPageError } from "@/lib/states/error-message";

export function AppRouteError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <PageError message={friendlyPageError(error)} onRetry={reset} />;
}
