"use client";

import type { RunConsoleSnapshot } from "@/lib/api/run-console";

export interface ArtifactLinksProps {
  artifacts: RunConsoleSnapshot["artifacts"];
}

export function ArtifactLinks({ artifacts }: ArtifactLinksProps) {
  if (artifacts.length === 0) {
    return null;
  }

  return (
    <section className="space-y-2">
      <h3 className="text-sm font-semibold">Artifacts</h3>
      <ul className="space-y-2 text-sm">
        {artifacts.map((artifact) => (
          <li key={artifact.attempt_index} className="rounded border border-border/60 p-2">
            <span className="font-medium">Attempt {artifact.attempt_index}</span>
            <div className="mt-1 flex flex-wrap gap-3 text-primary">
              {artifact.trace_url ? (
                <a href={artifact.trace_url} target="_blank" rel="noreferrer">
                  Trace (Playwright viewer)
                </a>
              ) : null}
              {artifact.video_url ? (
                <a href={artifact.video_url} target="_blank" rel="noreferrer">
                  Video
                </a>
              ) : null}
              {artifact.screenshot_url ? (
                <a href={artifact.screenshot_url} target="_blank" rel="noreferrer">
                  Screenshot
                </a>
              ) : null}
              {artifact.dom_url ? (
                <a href={artifact.dom_url} target="_blank" rel="noreferrer">
                  DOM snapshot
                </a>
              ) : null}
            </div>
          </li>
        ))}
      </ul>
    </section>
  );
}
