import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import type { AdminUserOperational } from "@/lib/api/admin-dashboard";
import { surface } from "@/lib/design/tokens";

function Row({ label, value }: { label: string; value: string }) {
  return (
    <div className="flex justify-between gap-4 border-b border-border/30 py-2 text-sm">
      <span className="text-muted-foreground">{label}</span>
      <span className="text-right font-medium tabular-nums">{value}</span>
    </div>
  );
}

export function AdminSupportView({
  data,
  isLoading,
  isError,
  onRetry,
  onClose,
}: {
  data: AdminUserOperational | undefined;
  isLoading: boolean;
  isError: boolean;
  onRetry: () => void;
  onClose: () => void;
}) {
  if (isLoading) return <PageLoading label="Loading support view…" />;
  if (isError || !data) {
    return <PageError message="Could not load support view." onRetry={onRetry} />;
  }

  const user = data.user as Record<string, string | null>;
  const tenant = data.tenant as Record<string, string>;
  const usage = data.usage_30d as {
    llm_cost_usd: number;
    needs_human_runs: number;
    runs_by_status: Record<string, number>;
  };

  return (
    <Card className={surface.card}>
      <CardHeader className="flex flex-row items-center justify-between">
        <CardTitle className="text-sm font-medium">Support view (audited)</CardTitle>
        <button
          type="button"
          className="text-xs text-muted-foreground underline-offset-2 hover:underline"
          onClick={onClose}
        >
          Close
        </button>
      </CardHeader>
      <CardContent className="space-y-4">
        <p className="text-xs text-muted-foreground">{data.privacy_note}</p>

        <div>
          <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Account
          </h3>
          <Row label="Email" value={user.email ?? "—"} />
          <Row label="Role" value={user.role ?? "—"} />
          <Row label="Status" value={user.status ?? "—"} />
          <Row label="Plan" value={tenant.plan ?? "—"} />
          <Row label="Last login" value={user.last_login_at?.slice(0, 19) ?? "Never"} />
        </div>

        <div>
          <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
            Usage (30d)
          </h3>
          <Row label="LLM cost" value={`$${usage.llm_cost_usd.toFixed(2)}`} />
          <Row label="Needs human" value={String(usage.needs_human_runs)} />
          {Object.entries(usage.runs_by_status ?? {}).map(([status, count]) => (
            <Row key={status} label={`Runs · ${status}`} value={String(count)} />
          ))}
        </div>

        {data.data_requests.length ? (
          <div>
            <h3 className="mb-1 text-xs font-medium uppercase tracking-wide text-muted-foreground">
              Privacy requests
            </h3>
            {data.data_requests.map((req) => {
              const row = req as { ts: string; action: string; message: string };
              return (
                <p key={row.ts + row.action} className="border-b border-border/30 py-1 text-xs">
                  <span className="text-foreground">{row.ts.slice(0, 19)}</span> — {row.action}:{" "}
                  {row.message}
                </p>
              );
            })}
          </div>
        ) : null}
      </CardContent>
    </Card>
  );
}
