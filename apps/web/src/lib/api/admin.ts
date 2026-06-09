import { apiFetch } from "@/lib/api/client";

export type AdminUser = {
  id: string;
  email: string;
  display_name: string | null;
  role: string;
  status: string;
  tenant_id: string;
  plan: string;
  last_login_at: string | null;
};

export type AdminAuditEntry = {
  id: string;
  actor_user_id: string;
  target_user_id: string | null;
  action: string;
  resource_type: string | null;
  resource_id: string | null;
  message: string;
  created_at: string;
};

export function fetchAdminUsers(): Promise<{ items: AdminUser[] }> {
  return apiFetch("/api/admin/users");
}

export function updateAdminUserRole(userId: string, role: "user" | "admin"): Promise<{ role: string }> {
  return apiFetch(`/api/admin/users/${userId}/role`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ role }),
  });
}

export function updateAdminUserStatus(
  userId: string,
  status: "active" | "suspended",
): Promise<{ status: string }> {
  return apiFetch(`/api/admin/users/${userId}/status`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ status }),
  });
}

export function fetchAdminAuditLog(): Promise<{ items: AdminAuditEntry[] }> {
  return apiFetch("/api/admin/audit-log");
}
