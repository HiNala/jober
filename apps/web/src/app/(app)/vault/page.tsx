import { Shield } from "lucide-react";

import { ProfileVault } from "@/components/vault/profile-vault";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export default function VaultPage() {
  return (
    <div className={cn(spacing.page, spacing.section, "mx-auto max-w-3xl")}>
      <header className="space-y-1">
        <div className="flex items-center gap-2">
          <Shield className="size-5 text-primary" aria-hidden />
          <h1 className="text-xl font-semibold tracking-tight">Vault</h1>
        </div>
        <p className="text-sm text-muted-foreground">
          Your resume, profile, and common answers — stored encrypted and used to ground every cover
          letter and form fill.
        </p>
      </header>

      <ProfileVault />
    </div>
  );
}
