import { afterEach, describe, expect, it, vi } from "vitest";

import { fetchLlmConfig } from "@/lib/api/llm";

describe("fetchLlmConfig", () => {
  afterEach(() => {
    vi.unstubAllGlobals();
  });

  it("returns provider and model list from API", async () => {
    vi.stubGlobal(
      "fetch",
      vi.fn().mockResolvedValue({
        ok: true,
        status: 200,
        json: async () => ({
          provider: "openai",
          default_model: "gpt-4o-mini",
          models: [{ id: "gpt-4o-mini", role: "draft", label: "Draft" }],
          budget_usd: 25,
        }),
      }),
    );

    const result = await fetchLlmConfig();
    expect(result.provider).toBe("openai");
    expect(result.default_model).toBe("gpt-4o-mini");
    expect(result.models).toHaveLength(1);
  });
});
