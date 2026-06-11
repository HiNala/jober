"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";

import { useUserPreferences } from "@/contexts/user-preferences-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { Label } from "@/components/ui/label";
import { fetchUsageDashboard } from "@/lib/api/billing";
import { fetchLlmConfig } from "@/lib/api/llm";
import {
  deleteProviderKey,
  fetchProviderKeys,
  upsertProviderKey,
} from "@/lib/api/preferences";
import { SettingsSection } from "@/components/settings/settings-section";

export function AiSettingsSection() {
  const { preferences, updatePreferences } = useUserPreferences();
  const [openaiKey, setOpenaiKey] = useState("");
  const queryClient = useQueryClient();
  const llmQuery = useQuery({ queryKey: ["llm-config"], queryFn: fetchLlmConfig });
  const usageQuery = useQuery({ queryKey: ["billing-usage"], queryFn: fetchUsageDashboard });
  const keysQuery = useQuery({ queryKey: ["provider-keys"], queryFn: fetchProviderKeys });

  const saveKeyMutation = useMutation({
    mutationFn: () => upsertProviderKey("openai", openaiKey),
    onSuccess: async () => {
      setOpenaiKey("");
      await queryClient.invalidateQueries({ queryKey: ["provider-keys"] });
    },
  });

  const deleteKeyMutation = useMutation({
    mutationFn: () => deleteProviderKey("openai"),
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["provider-keys"] });
    },
  });

  if (!preferences) return null;

  const openai = keysQuery.data?.items.find((k) => k.provider === "openai");

  return (
    <SettingsSection headingId="ai-heading" title="AI & providers">
      <p className="text-sm text-muted-foreground">
        Gateway provider: {llmQuery.data?.provider ?? "…"} · Budget used: $
        {usageQuery.data?.usage.llm_cost_usd.toFixed(2) ?? "0.00"} / $
        {usageQuery.data?.limits.max_llm_budget_usd.toFixed(0) ?? "—"}
      </p>

      <div className="mt-4 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="draft-model">Preferred draft model</Label>
          <select
            id="draft-model"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={preferences.ai.preferred_draft_model ?? llmQuery.data?.default_model ?? ""}
            onChange={(e) =>
              void updatePreferences({
                ai: { ...preferences.ai, preferred_draft_model: e.target.value || null },
              })
            }
          >
            <option value="">Gateway default</option>
            {llmQuery.data?.models.map((m) => (
              <option key={m.id} value={m.id}>
                {m.label} ({m.id})
              </option>
            ))}
          </select>
        </div>

        <div className="rounded-md border p-3">
          <p className="text-sm font-medium">Bring your own OpenAI key</p>
          <p className="text-xs text-muted-foreground">
            Stored encrypted server-side. Never sent to the browser after save.
          </p>
          {openai?.configured ? (
            <p className="mt-2 text-sm">
              Configured · hint …{openai.key_hint}
              <Button
                type="button"
                variant="ghost"
                size="sm"
                className="ml-2"
                onClick={() => deleteKeyMutation.mutate()}
              >
                Remove
              </Button>
            </p>
          ) : (
            <div className="mt-2 flex flex-wrap gap-2">
              <Input
                type="password"
                value={openaiKey}
                onChange={(e) => setOpenaiKey(e.target.value)}
                placeholder="sk-…"
                className="max-w-sm"
                autoComplete="off"
              />
              <Button
                type="button"
                size="sm"
                disabled={openaiKey.length < 8 || saveKeyMutation.isPending}
                onClick={() => saveKeyMutation.mutate()}
              >
                Save key
              </Button>
            </div>
          )}
        </div>
      </div>
    </SettingsSection>
  );
}
