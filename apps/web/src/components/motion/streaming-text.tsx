"use client";

import { motionStreamReveal } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface StreamingTextProps {
  text: string;
  className?: string;
  /** When true, play reveal animation (e.g. newly appended stream line). */
  reveal?: boolean;
}

/** Live agent output line — subtle reveal; instant under reduced-motion. */
export function StreamingText({ text, className, reveal = true }: StreamingTextProps) {
  return (
    <span className={cn(reveal && motionStreamReveal, className)}>{text}</span>
  );
}
