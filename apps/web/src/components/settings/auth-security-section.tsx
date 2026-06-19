"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { KeyRound, Link2, LogOut, Unlink } from "lucide-react";

import { toast } from "sonner";

import { useAuth } from "@/contexts/auth-context";
import { formatApiError } from "@/lib/api/errors";
import { isGoogleOAuthEnabled } from "@/lib/auth/google-oauth";
import { Button } from "@/components/ui/button";
import {
  fetchIdentities,
  fetchSessions,
  getGoogleLinkStartUrl,
  logoutAll,
  unlinkIdentity,
} from "@/lib/api/auth";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const PROVIDER_LABELS: Record<string, string> = {
  native: "Email & password",
  google: "Google",
  github: "GitHub",
};

export function AuthSecuritySection() {
  const { user, bypass, signOut } = useAuth();
  const queryClient = useQueryClient();
  const sessionsQuery = useQuery({
    queryKey: ["auth", "sessions"],
    queryFn: fetchSessions,
    enabled: !bypass && Boolean(user),
  });
  const identitiesQuery = useQuery({
    queryKey: ["auth", "identities"],
    queryFn: fetchIdentities,
    enabled: !bypass && Boolean(user),
  });

  const logoutAllMutation = useMutation({
    mutationFn: logoutAll,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["auth"] });
      await signOut();
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not revoke sessions")),
  });

  const unlinkMutation = useMutation({
    mutationFn: unlinkIdentity,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["auth", "identities"] });
      toast.success("Provider unlinked");
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not unlink provider")),
  });

  if (bypass || !user) {
    return null;
  }

  const activeCount = sessionsQuery.data?.active_sessions ?? 0;
  const identities = identitiesQuery.data?.items ?? [];
  const googleOAuthEnabled = isGoogleOAuthEnabled();
  const hasGoogle = identities.some((item) => item.provider === "google");
  const oauthCount = identities.filter((item) => item.provider !== "native").length;
  const hasPassword = identities.some((item) => item.provider === "native");
  const canUnlinkGoogle = hasGoogle && (hasPassword || oauthCount > 1);

  return (
    <section
      aria-labelledby="auth-security-heading"
      className={cn(surface.workspace, "p-4")}
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

      <div className="mt-4">
        <h3 className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          Sign-in methods
        </h3>
        <ul className="mt-2 space-y-2">
          {identitiesQuery.isLoading ? (
            <li className="text-sm text-muted-foreground">Loading linked accounts…</li>
          ) : (
            identities.map((identity) => (
              <li
                key={identity.provider}
                className="flex items-center justify-between gap-2 rounded-md border px-3 py-2 text-sm"
              >
                <div>
                  <p className="font-medium">
                    {PROVIDER_LABELS[identity.provider] ?? identity.provider}
                  </p>
                  <p className="text-xs text-muted-foreground">
                    {identity.provider_email ?? identity.display_name ?? "Linked"}
                  </p>
                </div>
                {identity.provider === "google" ? (
                  <Button
                    type="button"
                    variant="ghost"
                    size="sm"
                    disabled={!canUnlinkGoogle || unlinkMutation.isPending}
                    onClick={() => unlinkMutation.mutate("google")}
                  >
                    <Unlink className="mr-1 size-3.5" aria-hidden />
                    Unlink
                  </Button>
                ) : null}
              </li>
            ))
          )}
        </ul>
        {googleOAuthEnabled && !hasGoogle ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            className="mt-3"
            onClick={() => {
              window.location.href = getGoogleLinkStartUrl("/settings");
            }}
          >
            <Link2 className="mr-2 size-3.5" aria-hidden />
            Link Google account
          </Button>
        ) : null}
      </div>

      <dl className="mt-4 grid gap-2 text-sm sm:grid-cols-2">
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
      {logoutAllMutation.isError || unlinkMutation.isError ? (
        <p className="mt-2 text-xs text-destructive" role="alert">
          {unlinkMutation.isError
            ? "Could not unlink provider. Keep at least one sign-in method."
            : "Could not revoke sessions. Try again."}
        </p>
      ) : null}
    </section>
  );
}
