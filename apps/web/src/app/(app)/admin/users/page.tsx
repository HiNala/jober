"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { AdminRouteGuard } from "@/components/auth/admin-route-guard";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import {
  fetchAdminAuditLog,
  fetchAdminUsers,
  updateAdminUserRole,
  updateAdminUserStatus,
} from "@/lib/api/admin";
import { useAuth } from "@/contexts/auth-context";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

function AdminUsersPanel() {
  const { user: me } = useAuth();
  const queryClient = useQueryClient();
  const users = useQuery({ queryKey: ["admin-users"], queryFn: fetchAdminUsers });
  const audit = useQuery({ queryKey: ["admin-audit"], queryFn: fetchAdminAuditLog });

  const roleMutation = useMutation({
    mutationFn: ({ id, role }: { id: string; role: "user" | "admin" }) =>
      updateAdminUserRole(id, role),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      void queryClient.invalidateQueries({ queryKey: ["admin-audit"] });
    },
  });

  const statusMutation = useMutation({
    mutationFn: ({ id, status }: { id: string; status: "active" | "suspended" }) =>
      updateAdminUserStatus(id, status),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-users"] });
      void queryClient.invalidateQueries({ queryKey: ["admin-audit"] });
    },
  });

  if (users.isLoading) return <PageLoading label="Loading users…" />;
  if (users.isError || !users.data) {
    return <PageError message="Could not load admin users." onRetry={() => users.refetch()} />;
  }

  return (
    <div className={cn(spacing.section)}>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Admin — users</h1>
        <p className="text-sm text-muted-foreground">
          Operational directory only (email, role, status). Vault and job data stay tenant-scoped.
        </p>
      </div>

      <Card className={surface.card}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Accounts</CardTitle>
        </CardHeader>
        <CardContent className="overflow-x-auto">
          <table className="w-full text-xs">
            <thead>
              <tr className="text-left text-muted-foreground">
                <th className="py-1">Email</th>
                <th className="py-1">Role</th>
                <th className="py-1">Status</th>
                <th className="py-1">Actions</th>
              </tr>
            </thead>
            <tbody>
              {users.data.items.map((row) => (
                <tr key={row.id} className="border-t border-border/40">
                  <td className="py-2">{row.email}</td>
                  <td className="py-2 capitalize">{row.role}</td>
                  <td className="py-2 capitalize">{row.status}</td>
                  <td className="py-2">
                    <div className="flex flex-wrap gap-1">
                      {row.id !== me?.id && row.role === "user" ? (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={roleMutation.isPending}
                          onClick={() => roleMutation.mutate({ id: row.id, role: "admin" })}
                        >
                          Promote
                        </Button>
                      ) : null}
                      {row.id !== me?.id && row.role === "admin" ? (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={roleMutation.isPending}
                          onClick={() => roleMutation.mutate({ id: row.id, role: "user" })}
                        >
                          Demote
                        </Button>
                      ) : null}
                      {row.id !== me?.id && row.status === "active" ? (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={statusMutation.isPending}
                          onClick={() => statusMutation.mutate({ id: row.id, status: "suspended" })}
                        >
                          Suspend
                        </Button>
                      ) : null}
                      {row.status === "suspended" ? (
                        <Button
                          size="sm"
                          variant="outline"
                          disabled={statusMutation.isPending}
                          onClick={() => statusMutation.mutate({ id: row.id, status: "active" })}
                        >
                          Activate
                        </Button>
                      ) : null}
                    </div>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </CardContent>
      </Card>

      <Card className={surface.card}>
        <CardHeader>
          <CardTitle className="text-sm font-medium">Admin audit log</CardTitle>
        </CardHeader>
        <CardContent className="space-y-2 text-xs">
          {audit.isLoading ? <p className="text-muted-foreground">Loading audit…</p> : null}
          {audit.data?.items.map((entry) => (
            <p key={entry.id} className="border-b border-border/30 py-1 text-muted-foreground">
              <span className="text-foreground">{entry.created_at.slice(0, 19)}</span> —{" "}
              {entry.message}
            </p>
          ))}
        </CardContent>
      </Card>
    </div>
  );
}

export default function AdminUsersPage() {
  return (
    <AdminRouteGuard>
      <AdminUsersPanel />
    </AdminRouteGuard>
  );
}
