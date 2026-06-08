import Link from "next/link";

import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function AuthFormShell({
  title,
  subtitle,
  children,
  footer,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
}) {
  return (
    <div className={cn("mx-auto flex min-h-screen max-w-md flex-col justify-center p-6", motionFadeIn)}>
      <div className="mb-8 space-y-2 text-center">
        <Link href="/" className="text-sm font-semibold tracking-tight text-primary">
          Jober
        </Link>
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
      </div>
      <div className="rounded-xl border bg-card p-6 shadow-sm">{children}</div>
      {footer ? <div className="mt-4 text-center text-sm text-muted-foreground">{footer}</div> : null}
    </div>
  );
}
