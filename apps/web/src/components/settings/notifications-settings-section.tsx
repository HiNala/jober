"use client";

import { SettingsSection } from "@/components/settings/settings-section";

export function NotificationsSettingsSection() {
  return (
    <SettingsSection headingId="notifications-heading" title="Notifications">
      <p className="text-sm text-muted-foreground">
        In-app and email notifications for batch completion and run attention are not wired yet.
        Preferences will appear here once delivery is implemented.
      </p>
    </SettingsSection>
  );
}
