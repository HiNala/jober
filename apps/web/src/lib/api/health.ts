import { ApiError, apiFetch } from "@/lib/api/client";

export type ReadinessStatus = "ready" | "degraded" | "unknown";

export interface ReadinessResult {
  status: ReadinessStatus;
  detail?: string;
}

type ReadinessCheck = { ok: boolean; detail?: string };

type ReadyzResponse = {
  status: "ready" | "not_ready";
  checks?: Record<string, ReadinessCheck>;
};

function failedChecksDetail(report: ReadyzResponse): string | undefined {
  const failed = Object.entries(report.checks ?? {})
    .filter(([, check]) => !check.ok)
    .map(([name, check]) => `${name}: ${check.detail ?? "failed"}`);
  return failed.length > 0 ? failed.join("; ") : undefined;
}

export async function fetchReadiness(): Promise<ReadinessResult> {
  try {
    const report = await apiFetch<ReadyzResponse>("/readyz");
    if (report.status === "ready") {
      return { status: "ready" };
    }
    return {
      status: "degraded",
      detail: failedChecksDetail(report) ?? "Dependencies not ready",
    };
  } catch (error) {
    if (error instanceof ApiError && error.body) {
      try {
        const report = JSON.parse(error.body) as ReadyzResponse;
        const detail = failedChecksDetail(report);
        if (detail) {
          return { status: "degraded", detail };
        }
      } catch {
        // ignore malformed readiness bodies
      }
    }
    const message =
      error instanceof Error ? error.message : "Backend unreachable";
    return { status: "degraded", detail: message };
  }
}
