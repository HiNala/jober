"use client";

import { Lock, RefreshCw } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { motionShimmer, motionStatusEnter } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const LOCK_HELP =
  "Locked paragraphs are kept verbatim when you regenerate other paragraphs or the full letter.";

export function ParagraphControls({
  paragraphs,
  lockedParagraphs,
  onToggleLock,
  onRegenerate,
  regenPendingIndex,
  disabled,
}: {
  paragraphs: string[];
  lockedParagraphs: ReadonlySet<number>;
  onToggleLock: (index: number) => void;
  onRegenerate: (index: number) => void;
  regenPendingIndex?: number | null;
  disabled?: boolean;
}) {
  if (paragraphs.length === 0) {
    return null;
  }

  return (
    <TooltipProvider>
      <div className="space-y-2 border-t border-border pt-3">
        <div className="flex items-center gap-2">
          <p className="text-xs font-medium text-muted-foreground">Paragraph controls</p>
          <Tooltip>
            <TooltipTrigger
              type="button"
              className="text-muted-foreground hover:text-foreground"
              aria-label="How paragraph locking works"
            >
              <Lock className="size-3.5" aria-hidden />
            </TooltipTrigger>
            <TooltipContent className="max-w-xs text-xs">{LOCK_HELP}</TooltipContent>
          </Tooltip>
        </div>
        {paragraphs.map((para, index) => {
          const locked = lockedParagraphs.has(index);
          const regenPending = regenPendingIndex === index;
          return (
            <div
              key={index}
              className={cn(
                "flex flex-wrap items-start justify-between gap-2 rounded-md border p-2",
                locked ? "border-primary/30 bg-primary/5" : "border-border/50",
                regenPending && motionShimmer,
              )}
            >
              <p className="line-clamp-2 flex-1 text-xs text-muted-foreground">{para}</p>
              <div className="flex gap-2">
                <Button
                  type="button"
                  size="sm"
                  variant={locked ? "default" : "outline"}
                  className={locked ? motionStatusEnter : undefined}
                  disabled={disabled}
                  data-testid={`paragraph-lock-${index}`}
                  onClick={() => onToggleLock(index)}
                  aria-pressed={locked}
                >
                  <Lock className="mr-1 size-3.5" aria-hidden />
                  {locked ? "Locked" : "Lock"}
                </Button>
                <Button
                  type="button"
                  size="sm"
                  variant="outline"
                  disabled={disabled || locked || regenPending}
                  data-testid={`paragraph-regen-${index}`}
                  onClick={() => onRegenerate(index)}
                >
                  <RefreshCw className="mr-1 size-3.5" aria-hidden />
                  Regen
                </Button>
              </div>
            </div>
          );
        })}
      </div>
    </TooltipProvider>
  );
}
