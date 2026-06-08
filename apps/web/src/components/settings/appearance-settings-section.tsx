"use client";

import { useUserPreferences } from "@/contexts/user-preferences-context";
import { Label } from "@/components/ui/label";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export function AppearanceSettingsSection() {
  const { preferences, updatePreferences } = useUserPreferences();
  if (!preferences) return null;

  return (
    <section className={cn(surface.card, "rounded-lg p-4")} aria-labelledby="appearance-heading">
      <h2 id="appearance-heading" className="text-sm font-medium">
        Appearance
      </h2>
      <div className="mt-4 grid gap-4 sm:grid-cols-2">
        <div className="space-y-2">
          <Label htmlFor="theme-select">Theme</Label>
          <select
            id="theme-select"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={preferences.appearance.theme}
            onChange={(e) =>
              void updatePreferences({
                appearance: {
                  ...preferences.appearance,
                  theme: e.target.value as "light" | "dark" | "system",
                },
              })
            }
          >
            <option value="dark">Dark</option>
            <option value="light">Light</option>
          </select>
        </div>
        <div className="space-y-2">
          <Label htmlFor="density-select">Density</Label>
          <select
            id="density-select"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={preferences.appearance.density}
            onChange={(e) =>
              void updatePreferences({
                appearance: {
                  ...preferences.appearance,
                  density: e.target.value as "comfortable" | "compact",
                },
              })
            }
          >
            <option value="comfortable">Comfortable</option>
            <option value="compact">Compact</option>
          </select>
        </div>
        <div className="space-y-2 sm:col-span-2">
          <Label htmlFor="motion-select">Motion</Label>
          <select
            id="motion-select"
            className="w-full rounded-md border bg-background px-3 py-2 text-sm"
            value={
              preferences.appearance.reduced_motion === null
                ? "system"
                : preferences.appearance.reduced_motion
                  ? "reduce"
                  : "full"
            }
            onChange={(e) => {
              const value = e.target.value;
              const reduced =
                value === "system" ? null : value === "reduce";
              void updatePreferences({
                appearance: { ...preferences.appearance, reduced_motion: reduced },
              });
            }}
          >
            <option value="system">Follow system</option>
            <option value="reduce">Reduce motion</option>
            <option value="full">Full motion</option>
          </select>
        </div>
      </div>
    </section>
  );
}
