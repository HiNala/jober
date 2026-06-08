"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";

import { useUserPreferences } from "@/contexts/user-preferences-context";
import { Label } from "@/components/ui/label";
import { updateTenantPolicy } from "@/lib/api/preferences";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function ApplicationDefaultsSection({
  defaultRunPolicy,
  autoSubmitOptIn,
}: {
  defaultRunPolicy: string;
  autoSubmitOptIn: boolean;
}) {
  const { preferences, updatePreferences } = useUserPreferences();
  const queryClient = useQueryClient();

  const policyMutation = useMutation({
    mutationFn: updateTenantPolicy,
    onSuccess: async () => {
      await queryClient.invalidateQueries({ queryKey: ["tenant-policy"] });
    },
  });

  if (!preferences) return null;

  return (
    <section className={cn(surface.card, "rounded-lg p-4")} aria-labelledby="app-defaults-heading">
      <h2 id="app-defaults-heading" className="text-sm font-medium">
        Application defaults
      </h2>
      <div className="mt-4 space-y-4">
        <div className="space-y-2">
          <Label htmlFor="run-policy">Default submission policy</Label>
          <select
            id="run-policy"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={defaultRunPolicy}
            onChange={(e) =>
              policyMutation.mutate({ default_run_policy: e.target.value })
            }
          >
            <option value="review_before_submit">Review before submit</option>
            <option value="auto_submit">Auto submit (opt-in)</option>
          </select>
        </div>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={autoSubmitOptIn}
            onChange={(e) =>
              policyMutation.mutate({
                auto_submit_opt_in: e.target.checked,
                default_run_policy: e.target.checked ? "auto_submit" : "review_before_submit",
              })
            }
          />
          Allow auto_submit when policy permits (never the default)
        </label>
        <label className="flex items-center gap-2 text-sm">
          <input
            type="checkbox"
            checked={preferences.application_defaults.generate_cover_letter_per_run}
            onChange={(e) =>
              void updatePreferences({
                application_defaults: {
                  ...preferences.application_defaults,
                  generate_cover_letter_per_run: e.target.checked,
                },
              })
            }
          />
          Generate cover letter per run
        </label>
        <div className="space-y-2">
          <Label htmlFor="voice-preset">Cover letter voice</Label>
          <select
            id="voice-preset"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={preferences.application_defaults.voice_preset}
            onChange={(e) =>
              void updatePreferences({
                application_defaults: {
                  ...preferences.application_defaults,
                  voice_preset: e.target.value,
                },
              })
            }
          >
            <option value="professional">Professional</option>
            <option value="warm">Warm</option>
            <option value="concise">Concise</option>
          </select>
        </div>
      </div>
    </section>
  );
}
