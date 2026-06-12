"use client";

import { QueryClient, QueryClientProvider } from "@tanstack/react-query";
import { ThemeProvider } from "next-themes";
import { useState } from "react";

import { AnalyticsProvider } from "@/components/analytics/analytics-provider";
import { Toaster } from "@/components/ui/sonner";
import { TooltipProvider } from "@/components/ui/tooltip";
import { AuthProvider } from "@/contexts/auth-context";
import { UserPreferencesProvider } from "@/contexts/user-preferences-context";

/** Marketing + legal + blog — no React Query / auth session fetch on first paint. */
export function ShellProviders({ children }: { children: React.ReactNode }) {
  return (
    <ThemeProvider attribute="class" defaultTheme="dark" enableSystem={false}>
      <TooltipProvider delay={200}>
        <AnalyticsProvider>
          {children}
          <Toaster richColors closeButton position="top-right" />
        </AnalyticsProvider>
      </TooltipProvider>
    </ThemeProvider>
  );
}

/** Workspace + auth routes — session, preferences, and shared query cache. */
export function AppProviders({ children }: { children: React.ReactNode }) {
  const [queryClient] = useState(
    () =>
      new QueryClient({
        defaultOptions: {
          queries: {
            staleTime: 60_000,
            gcTime: 5 * 60_000,
            retry: 1,
            refetchOnWindowFocus: false,
          },
        },
      }),
  );

  return (
    <QueryClientProvider client={queryClient}>
      <AuthProvider>
        <UserPreferencesProvider>{children}</UserPreferencesProvider>
      </AuthProvider>
    </QueryClientProvider>
  );
}

/** Full stack — tests and legacy call sites only. */
export function Providers({ children }: { children: React.ReactNode }) {
  return (
    <ShellProviders>
      <AppProviders>{children}</AppProviders>
    </ShellProviders>
  );
}
