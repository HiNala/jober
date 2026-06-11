import { FILL_DIFF_MOCK_ROWS } from "@/lib/marketing/content";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

/** Static redacted fill-diff for marketing — not live run data. */
export function FillDiffMock({ className }: { className?: string }) {
  return (
    <div
      className={cn(
        "overflow-hidden rounded-lg border border-border/60 text-left",
        surface.terminal,
        className,
      )}
      aria-hidden
    >
      <div className="border-b border-border/40 px-3 py-2 text-[10px] font-medium uppercase tracking-wider text-muted-foreground">
        Fill diff — proposed vs actual
      </div>
      <div className="overflow-x-auto">
      <table className="w-full min-w-[16rem] text-[10px]">
        <thead>
          <tr className="text-muted-foreground">
            <th className="px-3 py-1.5 text-left font-medium">Field</th>
            <th className="px-3 py-1.5 text-left font-medium">Proposed</th>
            <th className="px-3 py-1.5 text-left font-medium">Actual</th>
          </tr>
        </thead>
        <tbody>
          {FILL_DIFF_MOCK_ROWS.map((row) => (
            <tr key={row.field} className="border-t border-border/30">
              <td className="px-3 py-1.5 font-medium">{row.field}</td>
              <td className="px-3 py-1.5 font-mono opacity-90">{row.proposed}</td>
              <td className="px-3 py-1.5 font-mono opacity-90">
                {row.actual}
                {row.matched ? (
                  <span className="ml-1 text-accent" aria-hidden>
                    ✓
                  </span>
                ) : null}
              </td>
            </tr>
          ))}
        </tbody>
      </table>
      </div>
    </div>
  );
}
