import Link from "next/link";
import { notFound } from "next/navigation";

import { EventTerminal } from "@/components/run-console/event-terminal";
import { MetricCards } from "@/components/dashboard/metric-cards";
import { FeaturesBento } from "@/components/marketing/features-bento";
import { PageEmpty, PageError, PageLoading } from "@/components/states/page-states";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Surface } from "@/components/ui/surface";
import { surface } from "@/lib/design/tokens";
import { cn } from "@/lib/utils";

const SAMPLE_EVENTS = [
  {
    id: "evt-1",
    seq: 1,
    ts: new Date().toISOString(),
    level: "info",
    event_type: "run.started",
    message: "Dry run queued",
    payload: {},
  },
  {
    id: "evt-2",
    seq: 2,
    ts: new Date().toISOString(),
    level: "info",
    event_type: "field.filled",
    message: "email",
    payload: { field_key: "email" },
  },
];

export default function KitchenSinkPage() {
  if (process.env.NODE_ENV === "production") {
    notFound();
  }

  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-4">
        <div className="mx-auto flex max-w-6xl items-center justify-between gap-4">
          <div>
            <h1 className="text-lg font-semibold">Kitchen sink</h1>
            <p className="text-sm text-muted-foreground">
              Dev-only component reference — not indexed for production.
            </p>
          </div>
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
            ← Landing
          </Link>
        </div>
      </header>

      <div className="mx-auto max-w-6xl space-y-16 p-6">
        <section className="space-y-6">
          <div>
            <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
              Surface families (Mission 10)
            </h2>
            <p className="mt-1 text-sm text-muted-foreground">
              Three deliberate tiers — marketing bento, workspace data, terminal live.
            </p>
          </div>
          <div className="grid gap-6 lg:grid-cols-3">
            <Surface family="marketing" padding="lg" className="space-y-2">
              <p className="font-mono text-[10px] uppercase tracking-widest text-accent">Marketing</p>
              <h3 className="text-lg font-semibold">Expressive bento</h3>
              <p className="text-sm text-muted-foreground">
                Larger radius, soft ring, gradients allowed on children.
              </p>
            </Surface>
            <Surface family="workspace" padding="md" className="space-y-2">
              <h3 className="text-sm font-medium">Workspace data</h3>
              <p className="text-sm text-muted-foreground">
                Dense panels, quiet borders, table-first density.
              </p>
              <div className="rounded-md border border-border/60 bg-muted/20 px-2 py-1 font-mono text-xs tabular-nums">
                queue_depth: 12
              </div>
            </Surface>
            <Surface family="terminal" padding="md" className="space-y-1">
              <p className={surface.terminalMuted}>[live] acme / staff engineer</p>
              <p>field.filled — email</p>
              <p>human.required — review submit</p>
            </Surface>
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
            Primitives
          </h2>
          <div className="flex flex-wrap gap-2">
            <Button>Primary</Button>
            <Button variant="outline">Outline</Button>
            <Button variant="secondary">Secondary</Button>
            <Button variant="destructive">Destructive</Button>
            <Badge>Default</Badge>
            <Badge variant="outline">Outline</Badge>
          </div>
          <Input placeholder="Input" className="max-w-sm" />
          <Skeleton className="h-10 w-64" />
        </section>

        <section className="space-y-4">
          <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
            States (workspace family)
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            <Card className={cn(surface.workspace)}>
              <CardHeader>
                <CardTitle className="text-sm">Loading</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <PageLoading />
              </CardContent>
            </Card>
            <Card className={cn(surface.workspace)}>
              <CardHeader>
                <CardTitle className="text-sm">Empty</CardTitle>
              </CardHeader>
              <CardContent>
                <PageEmpty title="Empty" description="Nothing here yet." />
              </CardContent>
            </Card>
            <Card className={cn(surface.workspace)}>
              <CardHeader>
                <CardTitle className="text-sm">Error</CardTitle>
              </CardHeader>
              <CardContent>
                <PageError message="Example failure" />
              </CardContent>
            </Card>
          </div>
        </section>

        <section className="space-y-4">
          <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
            Terminal family
          </h2>
          <EventTerminal
            events={[...SAMPLE_EVENTS]}
            streamKey="kitchen-sink"
            company="Acme"
            role="Staff Engineer"
          />
        </section>

        <section className="space-y-4">
          <h2 className="text-sm font-medium uppercase tracking-wide text-muted-foreground">
            Workspace composed
          </h2>
          <MetricCards />
        </section>

        <section className="overflow-hidden rounded-lg border">
          <h2 className="border-b px-4 py-2 text-sm font-medium">Marketing bento (preview)</h2>
          <div className="p-4">
            <FeaturesBento />
          </div>
        </section>
      </div>
    </div>
  );
}
