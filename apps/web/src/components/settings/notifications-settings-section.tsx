"use client";

import { useUserPreferences } from "@/contexts/user-preferences-context";
import { SettingsSection } from "@/components/settings/settings-section";

export function NotificationsSettingsSection() {
  const { preferences, updatePreferences } = useUserPreferences();
  if (!preferences) return null;

  const { notifications } = preferences;

  return (
    <SettingsSection headingId="notifications-heading" title="Notifications">
      <div className="space-y-3 text-sm">
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={notifications.in_app_run_attention}
            onChange={(e) =>
              void updatePreferences({
                notifications: {
                  ...notifications,
                  in_app_run_attention: e.target.checked,
                },
              })
            }
          />
          In-app when a run needs your attention
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={notifications.in_app_batch_complete}
            onChange={(e) =>
              void updatePreferences({
                notifications: {
                  ...notifications,
                  in_app_batch_complete: e.target.checked,
                },
              })
            }
          />
          In-app when a batch finishes
        </label>
        <label className="flex items-center gap-2">
          <input
            type="checkbox"
            checked={notifications.email_batch_complete}
            onChange={(e) =>
              void updatePreferences({
                notifications: {
                  ...notifications,
                  email_batch_complete: e.target.checked,
                },
              })
            }
          />
          Email when a batch finishes (optional)
        </label>
      </div>
    </SettingsSection>
  );
}
