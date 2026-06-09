"use client";

import { useAuth } from "@/contexts/auth-context";
import { PageError, PageLoading } from "@/components/states/page-states";
import { isAdmin } from "@/lib/auth/permissions";

export function AdminRouteGuard({ children }: { children: React.ReactNode }) {
  const { user, isLoading } = useAuth();

  if (isLoading) return <PageLoading label="Checking access…" />;
  if (!isAdmin(user)) {
    return (
      <PageError
        message="Admin access required. Contact an existing admin if you need operational access."
      />
    );
  }

  return <>{children}</>;
}
