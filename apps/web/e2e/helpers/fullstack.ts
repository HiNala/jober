import { test } from "@playwright/test";

/** Skip full-stack specs unless E2E_FULL_STACK=1 (local full stack or CI e2e job). */
export function requireFullStack(): void {
  test.skip(
    process.env.E2E_FULL_STACK !== "1",
    "Set E2E_FULL_STACK=1 with API, worker, fixture server, and Postgres running",
  );
}
