import { EventStream } from "@/components/dashboard/event-stream";
import { MetricCards } from "@/components/dashboard/metric-cards";
import { WorkerStatusPanel } from "@/components/dashboard/worker-status";

export default function DashboardPage() {
  return (
    <div className="space-y-6 p-4 md:p-6">
      <MetricCards />
      <div className="grid gap-4 lg:grid-cols-3">
        <div className="lg:col-span-2">
          <EventStream />
        </div>
        <WorkerStatusPanel />
      </div>
    </div>
  );
}
