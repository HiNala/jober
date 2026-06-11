import Link from "next/link";
import { AlertCircle } from "lucide-react";

import { buttonVariants } from "@/components/ui/button";
import { cn } from "@/lib/utils";

export function AuthEdgeState({
  title,
  description,
  actionHref,
  actionLabel,
  className,
}: {
  title: string;
  description: string;
  actionHref: string;
  actionLabel: string;
  className?: string;
}) {
  return (
    <div className={cn("space-y-4 text-center", className)} role="alert">
      <div className="mx-auto flex size-12 items-center justify-center rounded-full bg-destructive/10">
        <AlertCircle className="size-5 text-destructive" aria-hidden />
      </div>
      <div className="space-y-2">
        <h2 className="text-base font-medium">{title}</h2>
        <p className="text-sm text-muted-foreground">{description}</p>
      </div>
      <Link href={actionHref} className={buttonVariants({ size: "sm", variant: "outline" })}>
        {actionLabel}
      </Link>
    </div>
  );
}
