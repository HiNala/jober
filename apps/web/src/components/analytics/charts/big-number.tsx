import { cn } from "@/lib/utils";

export function BigNumber({
  label,
  value,
  hint,
  delta,
  className,
}: {
  label: string;
  value: string;
  hint?: string;
  delta?: string;
  className?: string;
}) {
  return (
    <div className={cn("space-y-1", className)}>
      <p className="text-xs text-muted-foreground">{label}</p>
      <p className="text-2xl font-semibold tabular-nums tracking-tight">{value}</p>
      {delta ? <p className="text-xs text-muted-foreground">{delta}</p> : null}
      {hint ? <p className="text-xs text-muted-foreground">{hint}</p> : null}
    </div>
  );
}
