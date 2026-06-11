import { CheckCircle2 } from "lucide-react";

import { cn } from "@/lib/utils";

export function AuthFormSuccess({
  title,
  description,
  action,
  className,
}: {
  title: string;
  description: string;
  action?: React.ReactNode;
  className?: string;
}) {
  return (
    <div className={cn("space-y-3 text-center", className)} role="status">
      <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-accent/15">
        <CheckCircle2 className="size-5 text-accent" aria-hidden />
      </div>
      <h2 className="text-base font-medium">{title}</h2>
      <p className="text-sm text-muted-foreground">{description}</p>
      {action ? <div className="pt-1">{action}</div> : null}
    </div>
  );
}
