"use client";

import { Pause, Pencil } from "lucide-react";

import { Button } from "@/components/ui/button";
import { motionView } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface ApproveSendBarProps {
  onApprove?: () => void;
  onEdit?: () => void;
  onPause?: () => void;
  approveLabel?: string;
  editLabel?: string;
  pauseLabel?: string;
  approveDisabled?: boolean;
  editDisabled?: boolean;
  pauseDisabled?: boolean;
  approvePending?: boolean;
  className?: string;
  /** Sticky bottom bar (default true). */
  sticky?: boolean;
}

/**
 * Sticky review footer: Approve & submit / Edit / Pause.
 */
export function ApproveSendBar({
  onApprove,
  onEdit,
  onPause,
  approveLabel = "Approve & submit",
  editLabel = "Edit",
  pauseLabel = "Pause",
  approveDisabled,
  editDisabled,
  pauseDisabled,
  approvePending,
  className,
  sticky = true,
}: ApproveSendBarProps) {
  return (
    <div
      className={cn(
        "border-t border-border/60 bg-background/90 px-4 py-3 backdrop-blur-md supports-backdrop-filter:bg-background/75",
        sticky && "sticky bottom-0 z-20 pb-[max(0.75rem,var(--safe-bottom))]",
        motionView,
        className,
      )}
      data-slot="approve-send-bar"
      role="region"
      aria-label="Review actions"
    >
      <div className="mx-auto flex max-w-3xl flex-wrap items-center justify-end gap-2">
        {onPause ? (
          <Button
            type="button"
            variant="ghost"
            size="sm"
            onClick={onPause}
            disabled={pauseDisabled}
          >
            <Pause className="size-3.5" aria-hidden />
            {pauseLabel}
          </Button>
        ) : null}
        {onEdit ? (
          <Button
            type="button"
            variant="outline"
            size="sm"
            onClick={onEdit}
            disabled={editDisabled}
          >
            <Pencil className="size-3.5" aria-hidden />
            {editLabel}
          </Button>
        ) : null}
        {onApprove ? (
          <Button
            type="button"
            size="sm"
            onClick={onApprove}
            disabled={approveDisabled || approvePending}
          >
            {approvePending ? "Submitting…" : approveLabel}
          </Button>
        ) : null}
      </div>
    </div>
  );
}
