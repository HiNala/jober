"use client";

import { useQueryClient } from "@tanstack/react-query";
import { toast } from "sonner";

import { ImportWizard } from "@/components/import/import-wizard";
import { attachImportToList } from "@/lib/api/discovery";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

type Props = {
  listId: string | null;
};

export function DiscoverUploadPanel({ listId }: Props) {
  const queryClient = useQueryClient();

  return (
    <div className={cn(surface.workspace, "rounded-lg p-4")}>
      <p className="mb-4 text-sm text-muted-foreground">
        Import your tracker workbook — jobs land in the same named list as board search results.
        {listId ? null : " Select or create a target list on the right first."}
      </p>
      <ImportWizard
        onCommitted={async (report) => {
          if (!listId) {
            toast.success("Import complete — select a list on the right to attach these jobs");
            return;
          }
          try {
            const result = await attachImportToList(listId, report.import_id);
            toast.success(`Attached ${result.attached} jobs to your list`);
            await queryClient.invalidateQueries({ queryKey: ["library", "job-lists"] });
            await queryClient.invalidateQueries({ queryKey: ["job-targets"] });
          } catch (err) {
            toast.error(err instanceof Error ? err.message : "Failed to attach import");
          }
        }}
      />
    </div>
  );
}
