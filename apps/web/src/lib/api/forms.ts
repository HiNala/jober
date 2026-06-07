import type { FieldObservationStatus, FormFieldObservationRead } from "@jober/schemas";

import { ApiError, apiFetch } from "@/lib/api/client";

export interface FormDiscoveryRead {
  run_id: string;
  attempt_id: string;
  platform: string | null;
  step_count: number;
  items: FormFieldObservationRead[];
}

export interface FormFieldObservationUpdate {
  mapped_profile_field?: string | null;
  status?: FieldObservationStatus;
  remember?: boolean;
  platform?: string;
}

export async function fetchFieldObservations(
  jobTargetId: string,
): Promise<FormFieldObservationRead[]> {
  try {
    const body = await apiFetch<{ items: FormFieldObservationRead[] }>(
      `/api/job-targets/${jobTargetId}/field-observations`,
    );
    return body.items;
  } catch (err: unknown) {
    if (err instanceof ApiError && err.status === 404) {
      return [];
    }
    throw err;
  }
}

export async function patchFieldObservation(
  observationId: string,
  update: FormFieldObservationUpdate,
): Promise<FormFieldObservationRead> {
  return apiFetch<FormFieldObservationRead>(
    `/api/job-targets/field-observations/${observationId}`,
    {
      method: "PATCH",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(update),
    },
  );
}
