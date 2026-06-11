import { MARKETING_PLANS } from "@/lib/marketing/plans";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const ROWS = [
  { label: "Monthly runs", key: "maxMonthlyRuns" as const },
  { label: "Batch size", key: "maxBatchItems" as const },
  { label: "Managed LLM budget", key: "maxLlmBudgetUsd" as const, format: (v: number) => `$${v}/mo` },
];

export function PlanComparisonTable({ className }: { className?: string }) {
  const free = MARKETING_PLANS[0];
  const pro = MARKETING_PLANS[1];

  return (
    <div className={cn(surface.card, "overflow-hidden rounded-xl", className)}>
      <table className="w-full text-sm">
        <caption className="sr-only">Plan feature comparison</caption>
        <thead>
          <tr className="border-b border-border/60 bg-muted/20 text-left">
            <th scope="col" className="px-4 py-3 font-medium text-muted-foreground">
              Limit
            </th>
            <th scope="col" className="px-4 py-3 font-semibold">
              {free.name}
            </th>
            <th scope="col" className="px-4 py-3 font-semibold">
              {pro.name}
            </th>
          </tr>
        </thead>
        <tbody>
          {ROWS.map(({ label, key, format }) => (
            <tr key={key} className="border-b border-border/40 last:border-0">
              <th scope="row" className="px-4 py-3 font-normal text-muted-foreground">
                {label}
              </th>
              <td className="px-4 py-3 font-medium tabular-nums">
                {format ? format(free.entitlements[key]) : free.entitlements[key]}
              </td>
              <td className="px-4 py-3 font-medium tabular-nums">
                {format ? format(pro.entitlements[key]) : pro.entitlements[key]}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}
