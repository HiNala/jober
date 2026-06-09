import { describe, expect, it } from "vitest";

import { can, isAdmin } from "@/lib/auth/permissions";

describe("permissions", () => {
  const user = {
    id: "1",
    email: "u@test.local",
    display_name: null,
    tenant_id: "t1",
    email_verified: true,
    status: "active",
    role: "user",
    plan: "free",
    last_login_at: null,
  };

  it("denies admin permissions for standard users", () => {
    expect(can(user, "admin:users:manage")).toBe(false);
    expect(isAdmin(user)).toBe(false);
  });

  it("grants admin permissions for admins", () => {
    const admin = { ...user, role: "admin" };
    expect(can(admin, "admin:audit:read")).toBe(true);
    expect(can(admin, "admin:ops:read")).toBe(true);
    expect(can(admin, "admin:config:manage")).toBe(true);
    expect(isAdmin(admin)).toBe(true);
  });
});
