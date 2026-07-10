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
    <div
      className={cn(
        "relative w-full rounded-xl border border-border/40 bg-card/80 p-1 text-card-foreground shadow-sm backdrop-blur-sm",
        motionFadeIn,
      )}
    >
      <div className="rounded-[calc(var(--radius)+2px)] px-1 py-1 sm:px-2 sm:py-2">
        <header className="mb-7 space-y-1.5 text-center lg:text-left">
          <h1 className="text-3xl font-semibold tracking-tight text-foreground">{title}</h1>
          {subtitle ? <p className="text-base text-muted-foreground">{subtitle}</p> : null}
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
        <div className="space-y-4">{children}</div>
        {footer ? (
          <p className="mt-6 text-center text-sm text-muted-foreground lg:text-left">{footer}</p>
        ) : null}
      </div>
    </div>
  );
}
