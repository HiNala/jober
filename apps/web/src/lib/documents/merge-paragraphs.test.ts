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

  it("keeps all locked paragraphs when every index is locked", () => {
    const original = ["A", "B"];
    const updated = ["X", "Y"];
    expect(mergeParagraphs(original, updated, new Set([0, 1]))).toEqual(["A", "B"]);
  });

  it("uses updated text when no paragraphs are locked", () => {
    expect(mergeParagraphs(["old"], ["new"], new Set())).toEqual(["new"]);
  });
});
