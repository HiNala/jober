"use client";

import { PageError } from "@/components/states/page-states";

export default function VaultError({
  error,
  reset,
}: {
  error: Error & { digest?: string };
  reset: () => void;
}) {
  return <PageError message={error.message} onRetry={reset} />;
}
