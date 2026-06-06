import Link from "next/link";

import { MetricCards } from "@/components/dashboard/metric-cards";
import { FileUpload } from "@/components/import/file-upload";
import { JobKanban } from "@/components/jobs/job-kanban";
import { MarketingHero } from "@/components/marketing/hero";
import { PageEmpty, PageError, PageLoading } from "@/components/states/page-states";
import { Badge } from "@/components/ui/badge";
import { Button } from "@/components/ui/button";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Input } from "@/components/ui/input";
import { Skeleton } from "@/components/ui/skeleton";
import { Tabs, TabsContent, TabsList, TabsTrigger } from "@/components/ui/tabs";

export default function KitchenSinkPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="border-b px-6 py-4">
        <div className="mx-auto flex max-w-5xl items-center justify-between">
          <h1 className="text-lg font-semibold">Kitchen sink</h1>
          <Link href="/" className="text-sm text-muted-foreground hover:text-foreground">
            ← Landing
          </Link>
        </div>
      </header>
      <div className="mx-auto max-w-5xl space-y-12 p-6">
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
            States
          </h2>
          <div className="grid gap-4 md:grid-cols-3">
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Loading</CardTitle>
              </CardHeader>
              <CardContent className="p-0">
                <PageLoading />
              </CardContent>
            </Card>
            <Card>
              <CardHeader>
                <CardTitle className="text-sm">Empty</CardTitle>
              </CardHeader>
              <CardContent>
                <PageEmpty title="Empty" description="Nothing here yet." />
              </CardContent>
            </Card>
            <Card>
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
            Composed
          </h2>
          <Tabs defaultValue="metrics">
            <TabsList>
              <TabsTrigger value="metrics">Metrics</TabsTrigger>
              <TabsTrigger value="kanban">Kanban</TabsTrigger>
              <TabsTrigger value="upload">Upload</TabsTrigger>
            </TabsList>
            <TabsContent value="metrics" className="mt-4">
              <MetricCards />
            </TabsContent>
            <TabsContent value="kanban" className="mt-4">
              <JobKanban />
            </TabsContent>
            <TabsContent value="upload" className="mt-4">
              <FileUpload />
            </TabsContent>
          </Tabs>
        </section>

        <section className="overflow-hidden rounded-lg border">
          <h2 className="border-b px-4 py-2 text-sm font-medium">Marketing hero (preview)</h2>
          <MarketingHero />
        </section>
      </div>
    </div>
  );
}
