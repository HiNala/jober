"use client";

import dynamic from "next/dynamic";
import { use } from "react";

import { RunConsoleSkeleton } from "@/components/states/page-states";

const RunConsole = dynamic(
  () => import("@/components/run-console/run-console").then((m) => m.RunConsole),
  { loading: () => <RunConsoleSkeleton />, ssr: false },
);

export default function RunConsolePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return (
    <div className="mx-auto max-w-6xl p-4 md:p-6">
      <RunConsole runId={id} />
    </div>
  );
}
