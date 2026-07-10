"use client";

import { useQuery, useQueryClient } from "@tanstack/react-query";
import { createContext, useCallback, useContext, useEffect, useMemo, useState } from "react";

import { ReAuthDialog } from "@/components/auth/re-auth-dialog";
import { type AuthUser, fetchMe, logout as apiLogout, refreshSession } from "@/lib/api/auth";
import { registerSessionHandlers } from "@/lib/api/session-recovery";

type AuthContextValue = {
  user: AuthUser | null;
  isLoading: boolean;
  isAuthenticated: boolean;
  bypass: boolean;
  signOut: () => Promise<void>;
  refresh: () => Promise<void>;
};

const AuthContext = createContext<AuthContextValue | null>(null);

const BYPASS =
  process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS === "true" ||
  process.env.NEXT_PUBLIC_AUTH_MODE === "dev";

const SILENT_REFRESH_MS = 30 * 60 * 1000;

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const queryClient = useQueryClient();
  const [sessionExpired, setSessionExpired] = useState(false);
  const meQuery = useQuery({
    queryKey: ["auth", "me"],
    queryFn: async () => {
      try {
        return await fetchMe();
      } catch {
        // Stale cookie: try silent refresh once, then re-auth UI.
        try {
          await refreshSession();
          return await fetchMe();
        } catch {
          setSessionExpired(true);
          return null;
        }
      }
    },
    retry: false,
    enabled: !BYPASS,
    staleTime: 60_000,
  });

  const signOut = useCallback(async () => {
    if (!BYPASS) {
      try {
        await apiLogout();
      } catch {
        // cookie may already be cleared
      }
    }
    queryClient.setQueryData(["auth", "me"], null);
    queryClient.clear();
    await queryClient.invalidateQueries({ queryKey: ["auth"] });
  }, [queryClient]);

  const refresh = useCallback(async () => {
    if (BYPASS) return;
    try {
      await refreshSession();
      await queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
    } catch {
      setSessionExpired(true);
    }
  }, [queryClient]);

  useEffect(() => {
    if (BYPASS) return;
    registerSessionHandlers(
      async () => {
        try {
          await refreshSession();
          await queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
          return true;
        } catch {
          return false;
        }
      },
      () => setSessionExpired(true),
    );
  }, [queryClient]);

  useEffect(() => {
    if (BYPASS || !meQuery.data) return;
    const timer = window.setInterval(() => {
      void refresh();
    }, SILENT_REFRESH_MS);
    return () => window.clearInterval(timer);
  }, [meQuery.data, refresh]);

  const value = useMemo<AuthContextValue>(
    () => ({
      user: BYPASS
        ? {
            id: "dev",
            email: "dev@jober.local",
            display_name: "Local Dev",
            tenant_id: "00000000-0000-4000-8000-000000000001",
            email_verified: true,
            status: "active",
            role: "user",
            plan: "pro",
            last_login_at: null,
          }
        : (meQuery.data ?? null),
      isLoading: !BYPASS && meQuery.isLoading,
      isAuthenticated: BYPASS || Boolean(meQuery.data),
      bypass: BYPASS,
      signOut,
      refresh,
    }),
    [meQuery.data, meQuery.isLoading, refresh, signOut],
  );

  return (
    <AuthContext.Provider value={value}>
      {children}
      {!BYPASS ? (
        <ReAuthDialog
          open={sessionExpired}
          emailHint={meQuery.data?.email}
          onSuccess={() => {
            setSessionExpired(false);
            void queryClient.invalidateQueries({ queryKey: ["auth", "me"] });
          }}
        />
      ) : null}
    </AuthContext.Provider>
  );
}

export function useAuth() {
  const ctx = useContext(AuthContext);
  if (!ctx) {
    throw new Error("useAuth must be used within AuthProvider");
  }
  return ctx;
}
