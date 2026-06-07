"use client";

import type { JobTargetRead } from "@jober/schemas";

import { Badge } from "@/components/ui/badge";
import {
  Drawer,
  DrawerContent,
  DrawerDescription,
  DrawerHeader,
  DrawerTitle,
} from "@/components/ui/drawer";
import { Textarea } from "@/components/ui/textarea";
import { DiscoveredFieldsPanel } from "@/components/jobs/discovered-fields-panel";
import { FailureReportPanel } from "@/components/jobs/failure-report-panel";
import { ReviewSubmitPanel } from "@/components/jobs/review-submit-panel";

export interface JobDetailDrawerProps {
  job: JobTargetRead | null;
  open: boolean;
  onOpenChange: (open: boolean) => void;
  onNotesChange?: (notes: string) => void;
}

export function JobDetailDrawer({
  job,
  open,
  onOpenChange,
  onNotesChange,
}: JobDetailDrawerProps) {
  if (!job) return null;

  return (
    <Drawer open={open} onOpenChange={onOpenChange}>
      <DrawerContent className="max-h-[85vh]">
        <DrawerHeader>
          <DrawerTitle>
            {job.company} — {job.role}
          </DrawerTitle>
          <DrawerDescription className="flex flex-wrap gap-2 pt-1">
            {job.priority && <Badge variant="outline">Priority {job.priority}</Badge>}
            {job.ats_guess && <Badge variant="secondary">{job.ats_guess}</Badge>}
            {job.needs_url && <Badge variant="destructive">Needs URL</Badge>}
          </DrawerDescription>
        </DrawerHeader>
        <div className="space-y-4 overflow-y-auto px-4 pb-6 text-sm">
          <dl className="grid gap-2 sm:grid-cols-2">
            <div>
              <dt className="text-muted-foreground">Location</dt>
              <dd>{job.location_work_style ?? "—"}</dd>
            </div>
            <div>
              <dt className="text-muted-foreground">Fit lane</dt>
              <dd>{job.fit_lane ?? "—"}</dd>
            </div>
            <div className="sm:col-span-2">
              <dt className="text-muted-foreground">Apply URL</dt>
              <dd className="break-all">
                {job.direct_apply_url ? (
                  <a
                    href={job.direct_apply_url}
                    className="text-primary underline-offset-4 hover:underline"
                    target="_blank"
                    rel="noreferrer"
                  >
                    {job.direct_apply_url}
                  </a>
                ) : (
                  "—"
                )}
              </dd>
            </div>
          </dl>
          <div>
            <label className="mb-1 block text-muted-foreground" htmlFor="job-notes">
              Notes
            </label>
            <Textarea
              id="job-notes"
              defaultValue={job.notes ?? ""}
              rows={4}
              onBlur={(e) => onNotesChange?.(e.target.value)}
            />
          </div>
          <FailureReportPanel jobTargetId={job.id} />
          <ReviewSubmitPanel
            jobTargetId={job.id}
            onEditField={() => {
              document.getElementById("discovered-fields-panel")?.scrollIntoView({
                behavior: "smooth",
              });
            }}
          />
          <div id="discovered-fields-panel">
            <h3 className="mb-2 text-sm font-medium">Discovered fields</h3>
            <DiscoveredFieldsPanel jobTargetId={job.id} platform={job.ats_guess} />
          </div>
        </div>
      </DrawerContent>
    </Drawer>
  );
}
