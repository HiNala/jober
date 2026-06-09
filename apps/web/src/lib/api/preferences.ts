import { apiFetch } from "@/lib/api/client";

export type UserPreferences = {
  appearance: {
    theme: "light" | "dark" | "system";
    density: "comfortable" | "compact";
    reduced_motion: boolean | null;
    canvas_view_mode: string;
    filmstrip_visible: boolean;
  };
  notifications: {
    in_app_run_attention: boolean;
    in_app_batch_complete: boolean;
    email_batch_complete: boolean;
  };
  application_defaults: {
    generate_cover_letter_per_run: boolean;
    letter_template?: string;
    voice_preset: string;
    site_cooldown_seconds: number | null;
  };
  ai: {
    preferred_draft_model: string | null;
    preferred_scoring_model: string | null;
  };
};

export type ProviderKeySummary = {
  provider: string;
  configured: boolean;
  key_hint: string | null;
};

export function fetchUserPreferences() {
  return apiFetch<{ preferences: UserPreferences }>("/api/settings/preferences");
}

export function patchUserPreferences(patch: Partial<UserPreferences>) {
  return apiFetch<{ preferences: UserPreferences }>("/api/settings/preferences", {
    method: "PATCH",
    body: JSON.stringify(patch),
  });
}

export function fetchProviderKeys() {
  return apiFetch<{ items: ProviderKeySummary[] }>("/api/settings/provider-keys");
}

export function upsertProviderKey(provider: string, apiKey: string) {
  return apiFetch<{ provider: string; configured: boolean; key_hint: string }>(
    `/api/settings/provider-keys/${provider}`,
    { method: "PUT", body: JSON.stringify({ api_key: apiKey }) },
  );
}

export function deleteProviderKey(provider: string) {
  return apiFetch<{ status: string }>(`/api/settings/provider-keys/${provider}`, {
    method: "DELETE",
  });
}

export function updateTenantPolicy(body: {
  default_run_policy?: string;
  auto_submit_opt_in?: boolean;
  retention_days?: number | null;
}) {
  return apiFetch<{ status: string }>("/api/settings/policy", {
    method: "PUT",
    body: JSON.stringify(body),
  });
}
