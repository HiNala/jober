"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KeyRound, LogOut } from "lucide-react";

import { useAuth } from "@/contexts/auth-context";
import { Button } from "@/components/ui/button";
import { fetchSessions, logoutAll } from "@/lib/api/auth";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function AuthSecuritySection() {
  const { user, bypass, signOut } = useAuth();
  const queryClient = useQueryClient();
  const sessionsQuery = useQuery({
    queryKey: ["auth", "sessions"],
    queryFn: fetchSessions,
    enabled: !bypass && Boolean(user),
  });

  const logoutAllMutation = useMutation({
    mutationFn: logoutAll,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["auth"] });
      await signOut();
    },
  });

  if (bypass || !user) {
    return null;
  }

  const activeCount = sessionsQuery.data?.active_sessions ?? 0;

  return (
    <section
      aria-labelledby="auth-security-heading"
      className={cn(surface.card, "rounded-lg p-4")}
    >
      <div className="mb-3 flex items-center gap-2">
        <KeyRound className="size-4 text-primary" aria-hidden />
        <h2 id="auth-security-heading" className="text-sm font-medium">
          Account security
        </h2>
      </div>
      <p className="text-sm text-muted-foreground">
        Signed in as <span className="font-medium text-foreground">{user.email}</span>
        {user.email_verified ? "" : " — verify your email to unlock all features"}
      </p>
      <dl className="mt-3 grid gap-2 text-sm sm:grid-cols-2">
        <div>
          <dt className="text-muted-foreground">Active sessions</dt>
          <dd className="font-medium tabular-nums">
            {sessionsQuery.isLoading ? "…" : activeCount}
          </dd>
        </div>
        <div>
          <dt className="text-muted-foreground">Role</dt>
          <dd className="font-medium capitalize">{user.role}</dd>
        </div>
      </dl>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={logoutAllMutation.isPending || activeCount <= 1}
          onClick={() => logoutAllMutation.mutate()}
        >
          <LogOut className="mr-2 size-3.5" aria-hidden />
          Sign out everywhere
        </Button>
        <Button type="button" variant="ghost" size="sm" onClick={() => void signOut()}>
          Sign out on this device
        </Button>
      </div>
      {logoutAllMutation.isError ? (
        <p className="mt-2 text-xs text-destructive" role="alert">
          Could not revoke sessions. Try again.
        </p>
      ) : null}
    </section>
  );
}
