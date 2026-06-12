import { isOpsDeskPath } from "@/lib/workspace/layout";

export type PageCommandId =
  | "import-spreadsheet"
  | "export-queue-xlsx"
  | "open-job-queue"
  | "toggle-canvas"
  | "toggle-focus-mode";

export type PageCommand = {
  id: PageCommandId;
  label: string;
};

/** Contextual commands for the workspace command palette (pathname-driven). */
export function buildPageCommands(
  pathname: string,
  options: { canvasOpen: boolean; focusMode: boolean },
): PageCommand[] {
  if (pathname === "/queue") {
    return [
      { id: "import-spreadsheet", label: "Import spreadsheet" },
      { id: "export-queue-xlsx", label: "Export queue XLSX" },
    ];
  }
  if (pathname === "/dashboard") {
    return [{ id: "open-job-queue", label: "Open job queue" }];
  }
  if (isOpsDeskPath(pathname)) {
    return [
      {
        id: "toggle-canvas",
        label: options.canvasOpen ? "Hide canvas" : "Show canvas",
      },
      {
        id: "toggle-focus-mode",
        label: options.focusMode ? "Exit focus mode" : "Enter focus mode",
      },
    ];
  }
  return [];
}
