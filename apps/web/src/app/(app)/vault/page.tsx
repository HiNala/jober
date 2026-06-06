"use client";

import { ProfileVault } from "@/components/vault/profile-vault";

export default function VaultPage() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <div>
        <h1 className="text-xl font-semibold tracking-tight">Profile vault</h1>
        <p className="text-sm text-muted-foreground">
          Resume, preferences, and encrypted EEO answers — sensitive fields never guessed.
        </p>
      </div>
      <ProfileVault />
    </div>
  );
}
