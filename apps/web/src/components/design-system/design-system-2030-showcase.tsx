"use client";

import * as React from "react";

import {
  AmbientCanvas,
  ApproveSendBar,
  CommandComposer,
  SkeletonStream,
  StatusLivePill,
  SuggestionChips,
  UnlockModal,
} from "@/components/design-system";
import { Button } from "@/components/ui/button";
import { cn } from "@/lib/utils";

/**
 * Dev-only kitchen-sink section for 2030 design primitives (M35).
 */
export function DesignSystem2030Showcase() {
  const [unlockOpen, setUnlockOpen] = React.useState(false);

  return (
    <section className="space-y-8" data-testid="design-system-2030">
      <div>
        <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
          2030 primitives (Mission 35)
        </h2>
        <p className="mt-1 text-sm text-muted-foreground">
          Hyperagent shell foundations — ambient canvas, stream skeletons, composer, approve bar,
          unlock modal.
        </p>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            AmbientCanvas
          </p>
          <AmbientCanvas className="h-40 rounded-xl border border-border/60" drift>
            <div className="flex h-full items-center justify-center">
              <p className="text-sm text-muted-foreground">Idle canvas wash</p>
            </div>
          </AmbientCanvas>
        </div>

        <div className="space-y-2">
          <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
            SkeletonStream
          </p>
          <div className="rounded-xl border border-border/60 bg-card/40 p-4">
            <SkeletonStream lines={5} align="mixed" />
          </div>
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          StatusLivePill
        </p>
        <div className="flex flex-wrap gap-2">
          <StatusLivePill status="live" />
          <StatusLivePill status="idle" />
          <StatusLivePill status="needs_you" />
        </div>
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          SuggestionChips
        </p>
        <SuggestionChips
          chips={[
            { id: "import", label: "Import tracker", href: "/queue" },
            { id: "discover", label: "Discover jobs", href: "/discover" },
            { id: "vault", label: "Open vault", href: "/vault" },
          ]}
        />
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          CommandComposer
        </p>
        <CommandComposer
          placeholder="What's the task?"
          onSubmit={() => {
            /* kitchen-sink presentational */
          }}
        />
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          UnlockModal
        </p>
        <Button type="button" variant="outline" size="sm" onClick={() => setUnlockOpen(true)}>
          Open unlock modal
        </Button>
        <UnlockModal open={unlockOpen} onOpenChange={setUnlockOpen} />
      </div>

      <div className="space-y-2">
        <p className="text-xs font-medium uppercase tracking-wide text-muted-foreground">
          ApproveSendBar
        </p>
        <div
          className={cn(
            "relative overflow-hidden rounded-xl border border-border/60",
            "bg-card/30",
          )}
        >
          <div className="space-y-2 p-4 text-sm text-muted-foreground">
            <p>Review package ready — sticky actions below.</p>
            <div className="h-16 rounded-md border border-dashed border-border/50" />
          </div>
          <ApproveSendBar
            sticky={false}
            onApprove={() => undefined}
            onEdit={() => undefined}
            onPause={() => undefined}
          />
        </div>
      </div>
    </section>
  );
}
