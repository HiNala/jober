import { motionFadeIn } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function AuthFormShell({
  title,
  subtitle,
  children,
  footer,
  bullets,
}: {
  title: string;
  subtitle?: string;
  children: React.ReactNode;
  footer?: React.ReactNode;
  bullets?: readonly string[];
}) {
  return (
    <div className={cn("w-full", motionFadeIn)}>
      <header className="mb-6 space-y-2 text-center lg:text-left">
        <h1 className="text-2xl font-semibold tracking-tight">{title}</h1>
        {subtitle ? <p className="text-sm text-muted-foreground">{subtitle}</p> : null}
        {bullets && bullets.length > 0 ? (
          <ul className="mt-3 space-y-1 text-left text-xs text-muted-foreground">
            {bullets.map((item) => (
              <li key={item} className="flex gap-2">
                <span className="text-accent" aria-hidden>
                  ·
                </span>
                <span>{item}</span>
              </li>
            ))}
          </ul>
        ) : null}
      </header>
      <div className="rounded-xl border border-border/60 bg-card p-6 shadow-sm">{children}</div>
      {footer ? (
        <p className="mt-4 text-center text-sm text-muted-foreground lg:text-left">{footer}</p>
      ) : null}
    </div>
  );
}
