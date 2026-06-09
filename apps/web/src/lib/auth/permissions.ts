import type { AuthUser } from "@/lib/api/auth";

export type Permission =
  | "authenticated"
  | "admin:analytics:read"
  | "admin:users:manage"
  | "admin:audit:read"
  | "admin:ops:read"
  | "admin:config:manage";

const ROLE_PERMISSIONS: Record<string, ReadonlySet<Permission>> = {
  user: new Set(["authenticated"]),
  admin: new Set([
    "authenticated",
    "admin:analytics:read",
    "admin:users:manage",
    "admin:audit:read",
    "admin:ops:read",
    "admin:config:manage",
  ]),
};

export function can(user: AuthUser | null | undefined, permission: Permission): boolean {
  if (!user) return false;
  return ROLE_PERMISSIONS[user.role]?.has(permission) ?? false;
}

export function isAdmin(user: AuthUser | null | undefined): boolean {
  return can(user, "admin:users:manage");
}
