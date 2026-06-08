import { apiFetch } from "@/lib/api/client";

export type DiscoveryCandidate = {
  candidate_key: string;
  company: string;
  role: string;
  direct_apply_url: string | null;
  company_careers_url: string | null;
  source: string;
  source_label: string;
  stage_signal: string | null;
  location_work_style: string | null;
  fit_score: number | null;
  ats_guess: string | null;
  existing_job_target_id: string | null;
  priority: string | null;
  fit_lane: string | null;
};

export type DiscoverySearchQuery = {
  role?: string;
  stack?: string[];
  location?: string;
  stage?: string;
  work_style?: string;
  board_urls?: string[];
  list_id?: string;
};

export type SavedSearch = {
  id: string;
  name: string;
  query: DiscoverySearchQuery;
  created_at: string;
  updated_at: string;
};

export function searchDiscovery(query: DiscoverySearchQuery) {
  return apiFetch<{ candidates: DiscoveryCandidate[] }>("/api/discovery/search", {
    method: "POST",
    body: JSON.stringify(query),
  });
}

export function acceptDiscoveryCandidates(body: {
  list_id: string;
  candidates: DiscoveryCandidate[];
  priority?: string;
  fit_lane?: string;
}) {
  return apiFetch<{ accepted: number; job_target_ids: string[] }>("/api/discovery/accept", {
    method: "POST",
    body: JSON.stringify(body),
  });
}

export function refreshDiscoveryList(listId: string) {
  return apiFetch<{ candidates: DiscoveryCandidate[] }>(
    `/api/discovery/lists/${listId}/refresh`,
    { method: "POST", body: "{}" },
  );
}

export function attachImportToList(listId: string, importId: string) {
  return apiFetch<{ attached: number }>(
    `/api/discovery/lists/${listId}/attach-import?import_id=${encodeURIComponent(importId)}`,
    { method: "POST", body: "{}" },
  );
}

export function fetchSavedSearches() {
  return apiFetch<{ items: SavedSearch[] }>("/api/discovery/saved-searches");
}

export function createSavedSearch(name: string, query: DiscoverySearchQuery) {
  return apiFetch<SavedSearch>("/api/discovery/saved-searches", {
    method: "POST",
    body: JSON.stringify({ name, query }),
  });
}

export function linkListSavedSearch(listId: string, savedSearchId: string | null) {
  return apiFetch<{ status: string }>(`/api/discovery/lists/${listId}/saved-search`, {
    method: "PATCH",
    body: JSON.stringify({ saved_search_id: savedSearchId }),
  });
}
