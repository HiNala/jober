"use client";

import dynamic from "next/dynamic";

import { useAuth } from "@/contexts/auth-context";
import { isAdmin } from "@/lib/auth/permissions";

const AdminAnalyticsPanel = dynamic(
  () =>
    import("@/components/analytics/admin-analytics-panel").then((mod) => ({
      default: mod.AdminAnalyticsPanel,
    })),
  { loading: () => <p className="text-sm text-muted-foreground">Loading analytics…</p> },
);
const UserAnalyticsPanel = dynamic(
  () =>
    import("@/components/analytics/user-analytics-panel").then((mod) => ({
      default: mod.UserAnalyticsPanel,
    })),
  { loading: () => <p className="text-sm text-muted-foreground">Loading analytics…</p> },
);
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { useState } from "react";

type Tab = "mine" | "admin";

export default function AnalyticsPage() {
  const { user } = useAuth();
  const showAdmin = isAdmin(user);
  const [tab, setTab] = useState<Tab>("mine");

  return (
    <div className={cn(spacing.page, spacing.section)}>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Analytics</h1>
        <p className="text-sm text-muted-foreground">
          First-party metrics from your workspace and product rollups. No third-party trackers.
        </p>
      </div>

      {showAdmin ? (
        <div className="flex gap-2" role="tablist" aria-label="Analytics views">
          <button
            type="button"
            role="tab"
            id="analytics-tab-mine"
            aria-selected={tab === "mine"}
            aria-controls="analytics-panel-mine"
            className={cn(
              "rounded-md px-3 py-1.5 text-sm",
              tab === "mine" ? "bg-primary text-primary-foreground" : "text-muted-foreground",
            )}
            onClick={() => setTab("mine")}
          >
            Your workspace
          </button>
          <button
            type="button"
            role="tab"
            id="analytics-tab-admin"
            aria-selected={tab === "admin"}
            aria-controls="analytics-panel-admin"
            className={cn(
              "rounded-md px-3 py-1.5 text-sm",
              tab === "admin" ? "bg-primary text-primary-foreground" : "text-muted-foreground",
            )}
            onClick={() => setTab("admin")}
          >
            Product (admin)
          </button>
        </div>
      ) : null}

      {tab === "admin" && showAdmin ? (
        <div role="tabpanel" id="analytics-panel-admin" aria-labelledby="analytics-tab-admin">
          <AdminAnalyticsPanel />
        </div>
      ) : (
        <div role="tabpanel" id="analytics-panel-mine" aria-labelledby="analytics-tab-mine">
          <UserAnalyticsPanel />
        </div>
      )}
    </div>
  );
}
