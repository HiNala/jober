import { describe, expect, it } from "vitest";

import { buildPageCommands } from "@/lib/workspace/command-palette-actions";

describe("buildPageCommands", () => {
  it("offers import and export on the queue page", () => {
    const commands = buildPageCommands("/queue", { canvasOpen: false, focusMode: false });
    expect(commands.map((c) => c.id)).toEqual(["import-spreadsheet", "export-queue-xlsx"]);
  });

  it("offers open queue from dashboard", () => {
    const commands = buildPageCommands("/dashboard", { canvasOpen: false, focusMode: false });
    expect(commands).toEqual([{ id: "open-job-queue", label: "Open job queue" }]);
  });

  it("offers canvas and focus toggles on run console routes", () => {
    const closed = buildPageCommands("/runs/abc", { canvasOpen: false, focusMode: false });
    expect(closed.map((c) => c.label)).toEqual(["Show canvas", "Enter focus mode"]);

    const open = buildPageCommands("/runs/abc", { canvasOpen: true, focusMode: true });
    expect(open.map((c) => c.label)).toEqual(["Hide canvas", "Exit focus mode"]);
  });

  it("returns no page commands on editorial routes", () => {
    expect(buildPageCommands("/settings", { canvasOpen: false, focusMode: false })).toEqual([]);
  });
});
