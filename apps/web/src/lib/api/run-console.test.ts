import { describe, expect, it, vi, beforeEach, afterEach } from "vitest";

import { fetchRecentRunEvents, fetchRunConsoleSnapshot } from "@/lib/api/run-console";

describe("run-console api helpers", () => {
  beforeEach(() => {
    vi.stubGlobal("fetch", vi.fn());
  });

  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("loads recent run events", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ items: [{ id: "e1", message: "run.started" }] }), {
        status: 200,
      }),
    );

    const items = await fetchRecentRunEvents();
    expect(items).toHaveLength(1);
    expect(items[0]?.message).toBe("run.started");
  });

  it("loads console snapshot for a run", async () => {
    vi.mocked(fetch).mockResolvedValue(
      new Response(JSON.stringify({ run_id: "run-1", events: [], timeline: [] }), {
        status: 200,
      }),
    );

    const snap = await fetchRunConsoleSnapshot("run-1");
    expect(snap.run_id).toBe("run-1");
  });
});
