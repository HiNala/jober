"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";

import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { PageError, PageLoading } from "@/components/states/page-states";
import { formatApiError } from "@/lib/api/errors";
import { fetchProductConfig, updateProductConfig } from "@/lib/api/admin-dashboard";
import { surface, spacing } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";
import { toast } from "sonner";

export function AdminConfigPanel() {
  const queryClient = useQueryClient();
  const config = useQuery({ queryKey: ["admin-config"], queryFn: fetchProductConfig });

  const saveMutation = useMutation({
    mutationFn: ({ key, value }: { key: string; value: Record<string, unknown> }) =>
      updateProductConfig(key, value),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey: ["admin-config"] });
      toast.success("Config saved");
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not save config")),
  });

  if (config.isLoading) return <PageLoading label="Loading config…" />;
  if (config.isError || !config.data) {
    return <PageError message="Could not load config." onRetry={() => config.refetch()} />;
  }

  return (
    <div className={cn(spacing.section)}>
      <div>
        <h1 className="text-lg font-semibold tracking-tight">Feature flags & config</h1>
        <p className="text-sm text-muted-foreground">
          Global defaults and toggles. Changes are audited.
        </p>
      </div>

      {config.data.items.map((entry) => (
        <Card key={entry.key} className={surface.card}>
          <CardHeader>
            <CardTitle className="text-sm font-medium">{entry.key.replace(/_/g, " ")}</CardTitle>
          </CardHeader>
          <CardContent className="space-y-3">
            <pre className="overflow-x-auto rounded-md bg-muted/50 p-3 text-xs">
              {JSON.stringify(entry.value, null, 2)}
            </pre>
            {entry.key === "feature_flags" ? (
              <div className="flex flex-wrap gap-2">
                {Object.entries(entry.value).map(([flag, enabled]) => {
                  const on = Boolean(enabled);
                  return (
                    <Button
                      key={flag}
                      size="sm"
                      variant={on ? "default" : "outline"}
                      disabled={saveMutation.isPending}
                      onClick={() =>
                        saveMutation.mutate({
                          key: entry.key,
                          value: { ...entry.value, [flag]: !on },
                        })
                      }
                    >
                      {flag}: {on ? "on" : "off"}
                    </Button>
                  );
                })}
              </div>
            ) : null}
            {entry.key === "announcement_banner" ? (
              <Button
                size="sm"
                variant="outline"
                disabled={saveMutation.isPending}
                onClick={() => {
                  const enabled = Boolean(entry.value.enabled);
                  saveMutation.mutate({
                    key: entry.key,
                    value: { ...entry.value, enabled: !enabled },
                  });
                }}
              >
                Banner: {entry.value.enabled ? "visible" : "hidden"}
              </Button>
            ) : null}
          </CardContent>
        </Card>
      ))}
    </div>
  );
}
