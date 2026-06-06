import { apiFetch } from "@/lib/api/client";

export type ReadinessStatus = "ready" | "degraded" | "unknown";

export interface ReadinessResult {
  status: ReadinessStatus;
  detail?: string;
}

export async function fetchReadiness(): Promise<ReadinessResult> {
  try {
    await apiFetch<Record<string, unknown>>("/readyz");
    return { status: "ready" };
  } catch (error) {
    const message =
      error instanceof Error ? error.message : "Backend unreachable";
    return { status: "degraded", detail: message };
  }
}
