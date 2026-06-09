"use client";

import { useQuery } from "@tanstack/react-query";
import { useState } from "react";

import { AttentionBanner } from "@/components/admin/attention-banner";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import { fetchAdminAuditLog } from "@/lib/api/admin";
import { fetchAdminDataRequests, fetchAdminSystem } from "@/lib/api/admin-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const AUDIT_ACTIONS = [
  { value: "", label: "All actions" },
  { value: "role_changed", label: "Role changed" },
  { value: "user_suspended", label: "User suspended" },
  { value: "user_activated", label: "User activated" },
  { value: "support_view_accessed", label: "Support view" },
  { value: "config_changed", label: "Config changed" },
];

export function AdminSystemPanel() {
  const [auditAction, setAuditAction] = useState("");
  const system = useQuery({ queryKey: ["admin-system"], queryFn: fetchAdminSystem });
  const audit = useQuery({
    queryKey: ["admin-audit", auditAction],
    queryFn: () => fetchAdminAuditLog({ limit: 100, action: auditAction || undefined }),
  });
  const dataRequests = useQuery({
    queryKey: ["admin-data-requests"],
    queryFn: fetchAdminDataRequests,
  });

  if (system.isLoading) return <PageLoading label="Loading system…" />;
  if (system.isError || !system.data) {
    return <PageError message="Could not load system." onRetry={() => system.refetch()} />;
  }

  const { health, attention } = system.data;

  return (
    <div className={cn(spacing.section)}>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">System & ops</h1>
        <p className="text-sm text-muted-foreground">
          Infrastructure health, queue state, audit trail, and privacy requests.
        </p>
      </div>

      <AttentionBanner items={attention} />

      <Card className={surface.card}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Infrastructure</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-sm">
          {Object.entries(health.checks).map(([name, check]) => (
            <div key={name} className="flex justify-between gap-4 border-b border-border/30 py-2">
              <span className="capitalize text-muted-foreground">{name}</span>
              <span className={check.ok ? "text-emerald-600" : "text-destructive"}>
                {check.ok ? "ok" : check.detail}
              </span>
            </div>
          ))}
          <div className="flex justify-between gap-4 py-2">
            <span className="text-muted-foreground">Queue paused</span>
            <span>{health.queue.globally_paused ? "Yes" : "No"}</span>
          </div>
          <div className="flex justify-between gap-4 py-2">
            <span className="text-muted-foreground">Active worker runs</span>
            <span className="tabular-nums">{health.queue.active_runs}</span>
          </div>
          <div className="flex justify-between gap-4 py-2">
            <span className="text-muted-foreground">Max concurrency</span>
            <span className="tabular-nums">{health.queue.max_concurrency}</span>
          </div>
        </CardContent>
      </Card>

      <Card className={surface.card}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Data export / delete requests</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-xs">
          {dataRequests.isLoading ? (
            <p className="text-muted-foreground">Loading…</p>
          ) : dataRequests.data?.items.length ? (
            dataRequests.data.items.map((row) => (
              <p key={row.id} className="border-b border-border/30 py-1 text-muted-foreground">
                <span className="text-foreground">{row.ts.slice(0, 19)}</span> — {row.action}:{" "}
                {row.message}
              </p>
            ))
          ) : (
            <p className="text-muted-foreground">No recent privacy requests.</p>
          )}
        </CardContent>
      </Card>

      <Card className={surface.card}>
        <CardHeader className="flex flex-row flex-wrap items-center justify-between gap-2">
          <CardTitle className="text-sm font-medium">Admin audit log</CardTitle>
          <select
            value={auditAction}
            onChange={(e) => setAuditAction(e.target.value)}
            className="rounded-md border border-input bg-background px-2 py-1 text-xs"
            aria-label="Filter audit by action"
          >
            {AUDIT_ACTIONS.map((opt) => (
              <option key={opt.value || "all"} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
        </CardHeader>
        <CardContent className="space-y-2 text-xs">
          {audit.isLoading ? (
            <p className="text-muted-foreground">Loading audit…</p>
          ) : (
            audit.data?.items.map((entry) => (
              <p key={entry.id} className="border-b border-border/30 py-1 text-muted-foreground">
                <span className="text-foreground">{entry.created_at.slice(0, 19)}</span> —{" "}
                {entry.action}: {entry.message}
              </p>
            ))
          )}
        </CardContent>
      </Card>
    </div>
  );
}
