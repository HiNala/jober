import { readFileSync } from "node:fs";
import { resolve } from "node:path";

import { describe, expect, it } from "vitest";

const TYPES_PATH = resolve(__dirname, "../../../../packages/schemas/generated/types.ts");

describe("@jober/schemas generated contract", () => {
  const content = readFileSync(TYPES_PATH, "utf-8");

  it("exports core enums used by the web app", () => {
    expect(content).toContain('export type RunStatus =');
    expect(content).toContain('export type JobTargetStatus =');
    expect(content).toContain("export interface JobTargetRead");
  });

  it("includes review_and_submit in RunStatus union", () => {
    expect(content).toContain('"review_and_submit"');
  });

  it("never exports auto_submit as a JobTargetStatus", () => {
    const jobBlock = content.slice(
      content.indexOf("export type JobTargetStatus"),
      content.indexOf("export interface JobTargetRead"),
    );
    expect(jobBlock).not.toContain("auto_submit");
  });
});
