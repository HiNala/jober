import { apiFetch } from "@/lib/api/client";

export function exportAllData() {
  return apiFetch<Record<string, unknown>>("/api/privacy/export-all");
}

export function deleteAllData(confirm: string) {
  return apiFetch<{ status: string }>("/api/privacy/delete-all", {
    method: "DELETE",
    body: JSON.stringify({ confirm }),
  });
}
