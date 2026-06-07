import { SettingsPanel } from "@/components/settings/settings-panel";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export default function SettingsPage() {
  return (
    <div className={cn(spacing.page, "mx-auto max-w-3xl")}>
      <SettingsPanel />
    </div>
  );
}
