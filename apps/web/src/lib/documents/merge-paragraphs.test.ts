import { describe, expect, it } from "vitest";

import { mergeParagraphs } from "@/lib/documents/merge-paragraphs";

describe("mergeParagraphs", () => {
  it("preserves locked paragraph text on regen", () => {
    const original = ["Opener", "Evidence", "Close"];
    const updated = ["New opener", "New evidence", "New close"];
    expect(mergeParagraphs(original, updated, new Set([1]))).toEqual([
      "New opener",
      "Evidence",
      "New close",
    ]);
  });
});
