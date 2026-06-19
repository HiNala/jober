"use client";

import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import type { DiscoveryCandidate } from "@/lib/api/discovery";

type Props = {
  candidates: DiscoveryCandidate[];
  selectedKeys: Set<string>;
  onToggle: (key: string) => void;
  onToggleAll: (checked: boolean) => void;
};

export function CandidateReview({ candidates, selectedKeys, onToggle, onToggleAll }: Props) {
  if (candidates.length === 0) {
    return (
      <p className="text-sm text-muted-foreground">
        Run a board search or refresh a saved list to review candidates here. Fit scores are
        advisory — you decide what enters the queue.
      </p>
    );
  }

  const allSelected = candidates.every((c) => selectedKeys.has(c.candidate_key));

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center justify-between gap-2">
        <h2 id="candidates-section-heading" className="text-sm font-medium">
          Candidates ({candidates.length})
        </h2>
        <label className="flex items-center gap-2 text-xs text-muted-foreground">
          <Checkbox
            checked={allSelected}
            onCheckedChange={(checked) => onToggleAll(Boolean(checked))}
          />
          Select all
        </label>
      </div>
      <ul className="divide-y divide-border rounded-lg border border-border">
        {candidates.map((candidate) => {
          const checked = selectedKeys.has(candidate.candidate_key);
          return (
            <li key={candidate.candidate_key} className="flex gap-3 p-3 text-sm">
              <Checkbox
                checked={checked}
                onCheckedChange={() => onToggle(candidate.candidate_key)}
                aria-label={`Select ${candidate.company} ${candidate.role}`}
                className="mt-1 shrink-0"
              />
              <div className="min-w-0 flex-1">
                <div className="flex flex-wrap items-center gap-2">
                  <p className="font-medium">
                    {candidate.company} — {candidate.role}
                  </p>
                  {candidate.fit_score != null ? (
                    <Badge variant="secondary">Fit {Math.round(candidate.fit_score)}</Badge>
                  ) : null}
                  {candidate.existing_job_target_id ? (
                    <Badge variant="outline">In tracker</Badge>
                  ) : null}
                </div>
                <p className="mt-1 text-xs text-muted-foreground">
                  Source: {candidate.source_label} ({candidate.source})
                  {candidate.ats_guess ? ` · ${candidate.ats_guess}` : ""}
                </p>
                {candidate.direct_apply_url ? (
                  <p className="mt-1 truncate text-xs text-muted-foreground">
                    {candidate.direct_apply_url}
                  </p>
                ) : null}
              </div>
            </li>
          );
        })}
      </ul>
    </div>
  );
}
