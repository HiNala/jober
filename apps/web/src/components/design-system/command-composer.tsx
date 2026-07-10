"use client";

import * as React from "react";
import { ArrowUp, ChevronDown, Paperclip } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  DropdownMenu,
  DropdownMenuContent,
  DropdownMenuItem,
  DropdownMenuTrigger,
} from "@/components/ui/dropdown-menu";
import { Textarea } from "@/components/ui/textarea";
import { motionMicro } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export interface CommandComposerPlanOption {
  id: string;
  label: string;
  description?: string;
}

export interface CommandComposerProps {
  value?: string;
  defaultValue?: string;
  onValueChange?: (value: string) => void;
  onSubmit?: (value: string) => void;
  placeholder?: string;
  /** Slot for attach control (file input trigger, etc.). */
  attachSlot?: React.ReactNode;
  planOptions?: CommandComposerPlanOption[];
  planValue?: string;
  onPlanChange?: (planId: string) => void;
  planLabel?: string;
  submitDisabled?: boolean;
  disabled?: boolean;
  className?: string;
  /** Accessible label for the composer region. */
  "aria-label"?: string;
}

const DEFAULT_PLANS: CommandComposerPlanOption[] = [
  { id: "auto", label: "Auto", description: "Best effort for this task" },
  { id: "careful", label: "Careful", description: "Extra review checkpoints" },
  { id: "fast", label: "Fast", description: "Fewer confirmation steps" },
];

/**
 * Presentational Hyperagent-style composer: textarea, attach, Plan dropdown, send.
 * Wire intents later — this shell does not call APIs.
 */
export function CommandComposer({
  value,
  defaultValue = "",
  onValueChange,
  onSubmit,
  placeholder = "What's the task?",
  attachSlot,
  planOptions = DEFAULT_PLANS,
  planValue,
  onPlanChange,
  planLabel = "Plan",
  submitDisabled,
  disabled,
  className,
  "aria-label": ariaLabel = "Command composer",
}: CommandComposerProps) {
  const [internal, setInternal] = React.useState(defaultValue);
  const [internalPlan, setInternalPlan] = React.useState(planOptions[0]?.id ?? "auto");
  const text = value ?? internal;
  const plan = planValue ?? internalPlan;
  const selected = planOptions.find((p) => p.id === plan) ?? planOptions[0];

  function setText(next: string) {
    if (value === undefined) setInternal(next);
    onValueChange?.(next);
  }

  function setPlan(id: string) {
    if (planValue === undefined) setInternalPlan(id);
    onPlanChange?.(id);
  }

  function handleSubmit() {
    const trimmed = text.trim();
    if (!trimmed || disabled || submitDisabled) return;
    onSubmit?.(trimmed);
  }

  return (
    <div
      className={cn(
        "rounded-2xl border border-border/70 bg-card/80 p-2 shadow-sm ring-1 ring-foreground/5 backdrop-blur-sm",
        motionMicro,
        className,
      )}
      data-slot="command-composer"
      role="group"
      aria-label={ariaLabel}
    >
      <Textarea
        value={text}
        onChange={(e) => setText(e.target.value)}
        placeholder={placeholder}
        disabled={disabled}
        rows={2}
        className="min-h-12 resize-none border-0 bg-transparent px-3 py-2 shadow-none focus-visible:ring-0 dark:bg-transparent"
        onKeyDown={(e) => {
          if (e.key === "Enter" && (e.metaKey || e.ctrlKey)) {
            e.preventDefault();
            handleSubmit();
          }
        }}
      />
      <div className="flex items-center justify-between gap-2 px-1 pt-1">
        <div className="flex items-center gap-1">
          {attachSlot ?? (
            <Button
              type="button"
              variant="ghost"
              size="icon-sm"
              disabled={disabled}
              aria-label="Attach"
            >
              <Paperclip className="size-4" aria-hidden />
            </Button>
          )}
          <DropdownMenu>
            <DropdownMenuTrigger
              disabled={disabled}
              render={
                <Button
                  type="button"
                  variant="ghost"
                  size="sm"
                  className="gap-1 text-muted-foreground"
                >
                  {planLabel}
                  {selected ? (
                    <span className="text-foreground/80">· {selected.label}</span>
                  ) : null}
                  <ChevronDown className="size-3.5 opacity-70" aria-hidden />
                </Button>
              }
            />
            <DropdownMenuContent align="start" className="min-w-48">
              {planOptions.map((option) => (
                <DropdownMenuItem
                  key={option.id}
                  onClick={() => setPlan(option.id)}
                  className={cn(option.id === plan && "bg-accent")}
                >
                  <div className="flex flex-col gap-0.5">
                    <span>{option.label}</span>
                    {option.description ? (
                      <span className="text-xs text-muted-foreground">{option.description}</span>
                    ) : null}
                  </div>
                </DropdownMenuItem>
              ))}
            </DropdownMenuContent>
          </DropdownMenu>
        </div>
        <Button
          type="button"
          size="icon-sm"
          disabled={disabled || submitDisabled || !text.trim()}
          onClick={handleSubmit}
          aria-label="Send"
          className="rounded-full"
        >
          <ArrowUp className="size-4" aria-hidden />
        </Button>
      </div>
    </div>
  );
}
