import { describe, expect, it, vi } from "vitest";

import {
  markSessionExpired,
  registerSessionHandlers,
  tryRecoverSession,
} from "@/lib/api/session-recovery";

describe("session-recovery", () => {
  it("invokes registered recover handler", async () => {
    const recover = vi.fn().mockResolvedValue(true);
    registerSessionHandlers(recover, () => undefined);
    await expect(tryRecoverSession()).resolves.toBe(true);
    expect(recover).toHaveBeenCalledOnce();
  });

  it("marks session expired via callback", () => {
    const onExpired = vi.fn();
    registerSessionHandlers(async () => false, onExpired);
    markSessionExpired();
    expect(onExpired).toHaveBeenCalledOnce();
  });
});
