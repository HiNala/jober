import { ProfileVault } from "@/components/vault/profile-vault";
import { PageHeader } from "@/components/app-shell/page-header";
import { spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

export default function VaultPage() {
  return (
    <div className={cn(spacing.page, spacing.section, "mx-auto max-w-3xl")}>
      <PageHeader
        title="Vault"
        description="Your resume, profile, and common answers — stored encrypted and used to ground every cover letter and form fill."
      />

      <ProfileVault />
    </div>
  );
}
