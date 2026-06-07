"use client";

import { useQuery } from "@tanstack/react-query";
import { Paperclip, Send } from "lucide-react";
import { useRef } from "react";

import { Button, buttonVariants } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import { Textarea } from "@/components/ui/textarea";
import { fetchLlmConfig } from "@/lib/api/llm";
import { motionMicro } from "@/lib/design/motion";
import { cn } from "@/lib/utils";
import { type CommandMode, useWorkspaceStore } from "@/stores/workspace-store";

function ModeToggle({
  mode,
  onChange,
}: {
  mode: CommandMode;
  onChange: (mode: CommandMode) => void;
}) {
  return (
    <div
      className="inline-flex rounded-md border bg-muted/40 p-0.5"
      role="group"
      aria-label="Command mode"
    >
      {(["plan", "execute"] as const).map((value) => (
        <button
          key={value}
          type="button"
          onClick={() => onChange(value)}
          className={cn(
            buttonVariants({ variant: mode === value ? "secondary" : "ghost", size: "xs" }),
            motionMicro,
            "capitalize",
          )}
          aria-pressed={mode === value}
        >
          {value}
        </button>
      ))}
    </div>
  );
}

export function WorkspaceCommandBar() {
  const inputRef = useRef<HTMLTextAreaElement>(null);
  const {
    commandMode,
    setCommandMode,
    commandDraft,
    setCommandDraft,
    selectedModel,
    setSelectedModel,
  } = useWorkspaceStore();

  const llmQuery = useQuery({
    queryKey: ["llm-config"],
    queryFn: fetchLlmConfig,
    staleTime: 60_000,
  });

  const models = llmQuery.data?.models ?? [];
  const activeModel = selectedModel ?? llmQuery.data?.default_model ?? models[0]?.id ?? "";

  return (
    <div className="shrink-0 border-t bg-background/95 p-3 backdrop-blur supports-[backdrop-filter]:bg-background/80">
      <form
        className="mx-auto flex max-w-3xl flex-col gap-2"
        onSubmit={(event) => {
          event.preventDefault();
        }}
      >
        <div className="flex items-end gap-2">
          <Button
            type="button"
            variant="outline"
            size="icon-sm"
            aria-label="Attach context"
            disabled
            title="Attachments arrive in a later mission"
          >
            <Paperclip className="size-4" />
          </Button>
          <Textarea
            ref={inputRef}
            id="workspace-command-input"
            value={commandDraft}
            onChange={(event) => setCommandDraft(event.target.value)}
            placeholder={
              commandMode === "plan"
                ? "Describe what you want to accomplish…"
                : "Issue a command for the active run…"
            }
            rows={2}
            className="min-h-[2.75rem] flex-1 resize-none"
            aria-label="Workspace command input"
          />
          <Button type="submit" size="icon-sm" aria-label="Send command" disabled={!commandDraft.trim()}>
            <Send className="size-4" />
          </Button>
        </div>
        <div className="flex flex-wrap items-center justify-between gap-2 px-1">
          <ModeToggle mode={commandMode} onChange={setCommandMode} />
          <div className="flex items-center gap-2">
            <span className="text-xs text-muted-foreground">Model</span>
            <Select
              value={activeModel}
              onValueChange={(value) => setSelectedModel(value ?? activeModel)}
              disabled={models.length === 0}
            >
              <SelectTrigger size="sm" className="w-[min(12rem,40vw)]" aria-label="LLM model">
                <SelectValue placeholder="Loading models…" />
              </SelectTrigger>
              <SelectContent>
                {models.map((model) => (
                  <SelectItem key={model.id} value={model.id}>
                    {llmQuery.data?.provider}/{model.id}
                  </SelectItem>
                ))}
              </SelectContent>
            </Select>
          </div>
        </div>
      </form>
    </div>
  );
}
