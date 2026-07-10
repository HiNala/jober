"use client";

import { useMutation } from "@tanstack/react-query";
import { useRouter } from "next/navigation";
import { useState } from "react";
import { toast } from "sonner";

import { useAuth } from "@/contexts/auth-context";
import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { formatApiError } from "@/lib/api/errors";
import { deleteAllData, exportAllData } from "@/lib/api/privacy";
import { SettingsSection } from "@/components/settings/settings-section";

export function PrivacyAccountSection() {
  const router = useRouter();
  const { signOut } = useAuth();
  const [confirm, setConfirm] = useState("");

  const exportMutation = useMutation({
    mutationFn: exportAllData,
    onSuccess: (data) => {
      const blob = new Blob([JSON.stringify(data, null, 2)], { type: "application/json" });
      const url = URL.createObjectURL(blob);
      const anchor = document.createElement("a");
      anchor.href = url;
      anchor.download = `jober-export-${new Date().toISOString().slice(0, 10)}.json`;
      anchor.click();
      URL.revokeObjectURL(url);
      toast.success("Export downloaded");
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Export failed — try again")),
  });

  const deleteMutation = useMutation({
    mutationFn: () => deleteAllData(confirm),
    onSuccess: async () => {
      await signOut();
      router.push("/login");
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not delete account data")),
  });

  return (
    <SettingsSection headingId="privacy-heading" title="Data & account">
      <p className="text-sm text-muted-foreground">
        Export everything tied to your tenant or permanently delete your data.
      </p>
      <div className="mt-4 flex flex-wrap gap-2">
        <Button
          type="button"
          variant="outline"
          size="sm"
          disabled={exportMutation.isPending}
          onClick={() => exportMutation.mutate()}
        >
          Export my data
        </Button>
      </div>
      <div className="mt-6 rounded-md border border-destructive/40 bg-destructive/5 p-3">
        <p className="text-sm font-medium text-destructive">Delete account data</p>
        <p className="mt-1 text-xs text-muted-foreground">
          Type DELETE ALL MY DATA to confirm. This removes jobs, runs, documents, and vault data.
        </p>
        <div className="mt-2 flex flex-wrap gap-2">
          <Input
            value={confirm}
            onChange={(e) => setConfirm(e.target.value)}
            placeholder="DELETE ALL MY DATA"
            className="max-w-xs"
            aria-label="Delete confirmation"
          />
          <Button
            type="button"
            variant="destructive"
            size="sm"
            disabled={confirm !== "DELETE ALL MY DATA" || deleteMutation.isPending}
            onClick={() => deleteMutation.mutate()}
          >
            Delete all data
          </Button>
        </div>
      </div>
    </SettingsSection>
  );
}
