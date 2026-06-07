"use client";

import { use } from "react";

import { RunConsole } from "@/components/run-console/run-console";

export default function RunConsolePage({ params }: { params: Promise<{ id: string }> }) {
  const { id } = use(params);
  return (
    <div className="mx-auto max-w-6xl space-y-4 p-6">
      <RunConsole runId={id} />
    </div>
  );
}
