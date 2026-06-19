"use client";

import dynamic from "next/dynamic";
import { use, useEffect } from "react";

import { track } from "@/lib/analytics/events";
import { RunOpsDeskShell } from "@/components/run-console/run-ops-desk-shell";
import { RunConsoleSkeleton } from "@/components/states/page-states";

const RunConsole = dynamic(
  () => import("@/components/run-console/run-console").then((m) => m.RunConsole),
  { loading: () => <RunConsoleSkeleton />, ssr: false },
);

export default function RunConsolePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);

  useEffect(() => {
    track("run.viewed", { run_id: id });
  }, [id]);
  return (
    <div className="flex h-full min-h-0 flex-col p-3 md:p-4">
      <RunOpsDeskShell>
        <RunConsole runId={id} />
      </RunOpsDeskShell>
    </div>
  );
}
