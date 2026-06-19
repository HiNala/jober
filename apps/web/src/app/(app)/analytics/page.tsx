"use client";

import { useState } from "react";
import dynamic from "next/dynamic";

import { useAuth } from "@/contexts/auth-context";
import { isAdmin } from "@/lib/auth/permissions";

import { PageLoading } from "@/components/states/page-states";
import { Tabs, TabsList, TabsTrigger } from "@/components/ui/tabs";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const AdminAnalyticsPanel = dynamic(
  () =>
    import("@/components/analytics/admin-analytics-panel").then((mod) => ({
      default: mod.AdminAnalyticsPanel,
    })),
  { loading: () => <PageLoading label="Loading analytics…" /> },
);
const UserAnalyticsPanel = dynamic(
  () =>
    import("@/components/analytics/user-analytics-panel").then((mod) => ({
      default: mod.UserAnalyticsPanel,
    })),
  { loading: () => <PageLoading label="Loading analytics…" /> },
);

type Tab = "mine" | "admin";

export default function AnalyticsPage() {
  const { user } = useAuth();
  const showAdmin = isAdmin(user);
  const [tab, setTab] = useState<Tab>("mine");

  return (
    <div className={cn(spacing.page, spacing.section)}>
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          First-party metrics from your workspace and product rollups. No third-party trackers.
        </p>
      </div>

      {showAdmin ? (
        <Tabs value={tab} onValueChange={(v) => setTab(v as Tab)}>
          <TabsList>
            <TabsTrigger value="mine">Your workspace</TabsTrigger>
            <TabsTrigger value="admin">Product (admin)</TabsTrigger>
          </TabsList>
        </Tabs>
      ) : null}

      {tab === "admin" && showAdmin ? (
        <AdminAnalyticsPanel />
      ) : (
        <UserAnalyticsPanel />
      )}
    </div>
  );
}
