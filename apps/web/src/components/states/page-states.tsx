import { AlertCircle, CheckCircle2, Inbox } from "lucide-react";

import { motionEmptyPulse, motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

import { Button } from "@/components/ui/button";
import { Skeleton } from "@/components/ui/skeleton";

export function PageLoading({ label = "Loading…" }: { label?: string }) {
  return (
    <div
      className={cn("flex flex-col gap-4 p-6", motionFadeIn)}
      role="status"
      aria-live="polite"
      aria-busy="true"
    >
      <span className="sr-only">{label}</span>
      <Skeleton className="h-7 w-56" />
      <div className="grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
        <Skeleton className="h-24 w-full" />
      </div>
      <Skeleton className="h-48 w-full" />
      <Skeleton className="h-32 w-full max-w-2xl" />
    </div>
  );
}

export function RunConsoleSkeleton() {
  return (
    <div className="space-y-4" role="status" aria-live="polite" aria-busy="true">
      <span className="sr-only">Loading run console</span>
      <div className="flex justify-between gap-4">
        <div className="space-y-2">
          <Skeleton className="h-6 w-64" />
          <Skeleton className="h-4 w-40" />
        </div>
        <Skeleton className="h-8 w-28" />
      </div>
      <div className="grid gap-4 lg:grid-cols-2">
        <Skeleton className="aspect-video w-full rounded-lg" />
        <Skeleton className="min-h-[240px] w-full rounded-lg" />
      </div>
    </div>
  );
}

export function PageEmpty({
  title,
  description,
  action,
  secondaryAction,
  icon,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
  secondaryAction?: React.ReactNode;
  icon?: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 px-6 py-16 text-center",
        motionFadeIn,
      )}
    >
      <div
        className={cn(
          "flex size-12 items-center justify-center rounded-full bg-muted",
          motionEmptyPulse,
        )}
      >
        {icon ?? <Inbox className="size-5 text-muted-foreground" aria-hidden />}
      </div>
      <h2 className="text-lg font-medium">{title}</h2>
      <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      {action ? <div className="flex flex-wrap items-center justify-center gap-2">{action}</div> : null}
      {secondaryAction ? (
        <div className="flex flex-wrap items-center justify-center gap-2">{secondaryAction}</div>
      ) : null}
    </div>
  );
}

export function PageError({
  title = "Something went wrong",
  message,
  onRetry,
}: {
  title?: string;
  message: string;
  onRetry?: () => void;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 px-6 py-16 text-center",
        motionFadeIn,
      )}
      role="alert"
    >
      <div className="flex size-12 items-center justify-center rounded-full bg-destructive/10">
        <AlertCircle className="size-5 text-destructive" aria-hidden />
      </div>
      <h2 className="text-lg font-medium">{title}</h2>
      <p className="max-w-md text-sm text-muted-foreground">{message}</p>
      {onRetry ? (
        <Button variant="outline" size="sm" onClick={onRetry}>
          Try again
        </Button>
      ) : null}
    </div>
  );
}

export function PageSuccess({
  title,
  description,
  action,
}: {
  title: string;
  description?: string;
  action?: React.ReactNode;
}) {
  return (
    <div
      className={cn(
        "flex flex-col items-center justify-center gap-3 px-6 py-12 text-center",
        motionFadeIn,
      )}
      role="status"
    >
      <div className="flex size-12 items-center justify-center rounded-full bg-accent/15">
        <CheckCircle2 className="size-5 text-accent" aria-hidden />
      </div>
      <h2 className="text-lg font-medium">{title}</h2>
      {description ? (
        <p className="max-w-md text-sm text-muted-foreground">{description}</p>
      ) : null}
      {action}
    </div>
  );
}
