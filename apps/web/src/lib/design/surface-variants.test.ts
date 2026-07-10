import { describe, expect, it } from "vitest";

import { surfaceFamilyClasses, surfaceVariants } from "@/lib/design/surface-variants";

describe("surfaceVariants", () => {
  it("defines three distinct families", () => {
    const marketing = surfaceVariants({ family: "marketing" });
    const workspace = surfaceVariants({ family: "workspace" });
    const terminal = surfaceVariants({ family: "terminal" });

    expect(marketing).toContain("rounded-2xl");
    expect(workspace).toContain("rounded-xl");
    expect(terminal).toContain("font-mono");
    expect(marketing).not.toBe(workspace);
    expect(workspace).not.toBe(terminal);
  });

  it("applies padding variants", () => {
    expect(surfaceVariants({ family: "workspace", padding: "md" })).toContain("p-4");
  });

  it("exports stable family class strings", () => {
    expect(surfaceFamilyClasses.marketing).toBe(surfaceVariants({ family: "marketing" }));
    expect(surfaceFamilyClasses.workspace).toBe(surfaceVariants({ family: "workspace" }));
    expect(surfaceFamilyClasses.terminal).toBe(surfaceVariants({ family: "terminal" }));
  });
});
