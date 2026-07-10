"use client";

import { useUserPreferences } from "@/contexts/user-preferences-context";

import { Checkbox } from "@/components/ui/checkbox";
import { Label } from "@/components/ui/label";
import { SettingsSection } from "@/components/settings/settings-section";

export function NotificationsSettingsSection() {
  const { preferences, updatePreferences, isLoading } = useUserPreferences();
  if (isLoading) {
    return (
      <SettingsSection headingId="notifications-heading" title="Notifications">
        <p className="text-sm text-muted-foreground">Loading preferences…</p>
      </SettingsSection>
    );
  }
  if (!preferences) {
    return (
      <SettingsSection headingId="notifications-heading" title="Notifications">
        <p className="text-sm text-muted-foreground">
          Sign in to configure in-app and email notification preferences.
        </p>
      </SettingsSection>
    );
  }

  const { notifications } = preferences;

  return (
    <SettingsSection headingId="notifications-heading" title="Notifications">
      <p className="text-sm text-muted-foreground">
        In-app toasts appear while you have Jober open. Email batch alerts require SMTP on the
        API (see Settings → email delivery).
      </p>
      <div className="mt-4 space-y-4">
        <div className="flex items-start gap-3">
          <Checkbox
            id="notify-run-attention"
            checked={notifications.in_app_run_attention}
            onCheckedChange={(checked) =>
              void updatePreferences({
                notifications: {
                  ...notifications,
                  in_app_run_attention: checked === true,
                },
              })
            }
          />
          <div className="grid gap-1">
            <Label htmlFor="notify-run-attention">Run needs attention</Label>
            <p className="text-xs text-muted-foreground">
              Show the dashboard banner when a run is waiting for your review.
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Checkbox
            id="notify-batch-complete"
            checked={notifications.in_app_batch_complete}
            onCheckedChange={(checked) =>
              void updatePreferences({
                notifications: {
                  ...notifications,
                  in_app_batch_complete: checked === true,
                },
              })
            }
          />
          <div className="grid gap-1">
            <Label htmlFor="notify-batch-complete">Batch finished (in-app)</Label>
            <p className="text-xs text-muted-foreground">
              Toast when a batch you started completes while this tab is open.
            </p>
          </div>
        </div>
        <div className="flex items-start gap-3">
          <Checkbox
            id="notify-email-batch"
            checked={notifications.email_batch_complete}
            onCheckedChange={(checked) =>
              void updatePreferences({
                notifications: {
                  ...notifications,
                  email_batch_complete: checked === true,
                },
              })
            }
          />
          <div className="grid gap-1">
            <Label htmlFor="notify-email-batch">Batch finished (email)</Label>
            <p className="text-xs text-muted-foreground">
              Email when a batch completes. Delivered only when SMTP is configured on the API;
              otherwise the preference is saved for when email is enabled.
            </p>
          </div>
        </div>
      </div>
    </SettingsSection>
  );
}
