"use client";

import {
  motionStatusEnter,
  runStatusTone,
  statusToneClasses,
  type RunStatusTone,
} from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface StatusPillProps {
  status: string;
  label?: string;
  className?: string;
  icon?: React.ReactNode;
}

/** Coordinated status pill — re-animates on lifecycle transitions. */
export function StatusPill({ status, label, className, icon }: StatusPillProps) {
  const tone: RunStatusTone = runStatusTone(status);
  const display = label ?? status.replace(/_/g, " ");

  return (
    <span
      key={`${tone}-${display}`}
      className={cn(
        "inline-flex h-5 items-center gap-1 rounded-full border px-2 py-0.5 text-xs font-medium capitalize tabular-nums",
        statusToneClasses[tone],
        motionStatusEnter,
        className,
      )}
    >
      {icon}
      {display}
    </span>
  );
}
