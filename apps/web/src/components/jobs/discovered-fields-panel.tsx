"use client";

import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { HelpCircle } from "lucide-react";
import { useMemo } from "react";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import {
  Select,
  SelectContent,
  SelectItem,
  SelectTrigger,
  SelectValue,
} from "@/components/ui/select";
import {
  Table,
  TableBody,
  TableCell,
  TableHead,
  TableHeader,
  TableRow,
} from "@/components/ui/table";
import {
  fetchFieldObservations,
  patchFieldObservation,
  type FormFieldObservationUpdate,
} from "@/lib/api/forms";
import { formatApiError } from "@/lib/api/errors";
import type { FieldObservationStatus, FormFieldObservationRead } from "@jober/schemas";

const PROFILE_FIELD_OPTIONS = [
  "name",
  "email",
  "phone",
  "location",
  "current_title",
  "links",
  "relocation_pref",
  "notice_period",
  "salary_prefs",
  "work_authorization",
  "sponsorship_needed",
  "veteran_status",
  "race_ethnicity",
  "gender",
  "disability",
  "resume_upload",
  "cover_letter_upload",
  "why_this_company",
  "about_yourself",
  "unknown",
] as const;

const STATUS_OPTIONS: FieldObservationStatus[] = [
  "skipped",
  "needs_review",
  "filled",
  "failed",
];

function confidenceTone(confidence: number | null | undefined): string {
  if (confidence == null) return "text-muted-foreground";
  if (confidence >= 0.82) return "text-emerald-600";
  if (confidence >= 0.65) return "text-amber-600";
  return "text-rose-600";
}

export interface DiscoveredFieldsPanelProps {
  jobTargetId: string;
  platform?: string | null;
}

export function DiscoveredFieldsPanel({ jobTargetId, platform }: DiscoveredFieldsPanelProps) {
  const queryClient = useQueryClient();
  const queryKey = useMemo(() => ["field-observations", jobTargetId], [jobTargetId]);

  const observationsQuery = useQuery({
    queryKey,
    queryFn: () => fetchFieldObservations(jobTargetId),
    enabled: Boolean(jobTargetId),
  });

  const patchMutation = useMutation({
    mutationFn: ({
      id,
      update,
    }: {
      id: string;
      update: FormFieldObservationUpdate;
    }) => patchFieldObservation(id, update),
    onSuccess: () => {
      void queryClient.invalidateQueries({ queryKey });
      toast.success("Field mapping updated");
    },
    onError: (err: unknown) => toast.error(formatApiError(err, "Could not update field")),
  });

  const items = observationsQuery.data ?? [];
  const reviewCount = items.filter((i) => i.status === "needs_review").length;
  const autoCount = items.filter((i) => i.status === "skipped").length;

  if (observationsQuery.isLoading) {
    return <p className="text-sm text-muted-foreground">Loading discovered fields…</p>;
  }

  if (observationsQuery.isError) {
    return (
      <p className="text-sm text-destructive">
        Could not load field observations.{" "}
        <button
          type="button"
          className="underline"
          onClick={() => void observationsQuery.refetch()}
        >
          Retry
        </button>
      </p>
    );
  }

  if (items.length === 0) {
    return (
      <div className="rounded-md border border-dashed border-border/70 p-4 text-sm text-muted-foreground">
        <p className="flex items-center gap-2 font-medium text-foreground">
          <HelpCircle className="size-4" aria-hidden />
          No discovered fields yet
        </p>
        <p className="mt-1">
          Form discovery runs when you start an application on the apply URL. Review mapped values
          here before auto-fill.
        </p>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      <div className="flex flex-wrap items-center gap-2 text-xs text-muted-foreground">
        <span>{items.length} fields</span>
        <span aria-hidden>·</span>
        <span className="text-emerald-600">{autoCount} eligible for auto-fill</span>
        <span aria-hidden>·</span>
        <span className="text-amber-600">{reviewCount} need review</span>
      </div>
      <Table>
        <TableHeader>
          <TableRow>
            <TableHead>Label</TableHead>
            <TableHead>Type</TableHead>
            <TableHead>Required</TableHead>
            <TableHead>Mapped to</TableHead>
            <TableHead>Preview</TableHead>
            <TableHead>Confidence</TableHead>
            <TableHead>Status</TableHead>
          </TableRow>
        </TableHeader>
        <TableBody>
          {items.map((row) => (
            <FieldRow
              key={row.id}
              row={row}
              platform={platform}
              disabled={patchMutation.isPending}
              onPatch={(update) => patchMutation.mutate({ id: row.id, update })}
            />
          ))}
        </TableBody>
      </Table>
    </div>
  );
}

interface FieldRowProps {
  row: FormFieldObservationRead;
  platform?: string | null;
  disabled: boolean;
  onPatch: (update: FormFieldObservationUpdate) => void;
}

function FieldRow({ row, platform, disabled, onPatch }: FieldRowProps) {
  return (
    <TableRow>
      <TableCell className="max-w-[140px] truncate font-medium" title={row.label ?? row.field_key}>
        {row.label ?? row.field_key}
      </TableCell>
      <TableCell className="text-muted-foreground">{row.field_type ?? "—"}</TableCell>
      <TableCell>{row.required ? "Yes" : "—"}</TableCell>
      <TableCell>
        <Select
          value={row.mapped_profile_field ?? "unknown"}
          disabled={disabled}
          onValueChange={(value) =>
            onPatch({
              mapped_profile_field: value === "unknown" ? null : value,
              platform: platform ?? "generic",
              remember: true,
            })
          }
        >
          <SelectTrigger className="h-8 w-[140px]" aria-label={`Map ${row.label ?? row.field_key}`}>
            <SelectValue />
          </SelectTrigger>
          <SelectContent>
            {PROFILE_FIELD_OPTIONS.map((key) => (
              <SelectItem key={key} value={key}>
                {key}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
      </TableCell>
      <TableCell className="max-w-[120px] truncate font-mono text-xs text-muted-foreground">
        {row.proposed_value_redacted ?? "—"}
      </TableCell>
      <TableCell className={confidenceTone(row.confidence)}>
        {row.confidence != null ? `${Math.round(row.confidence * 100)}%` : "—"}
      </TableCell>
      <TableCell>
        <div className="flex items-center gap-2">
          <Select
            value={row.status}
            disabled={disabled}
            onValueChange={(value) =>
              onPatch({
                status: value as FieldObservationStatus,
                platform: platform ?? "generic",
              })
            }
          >
            <SelectTrigger className="h-8 w-[130px]" aria-label={`Status for ${row.label ?? row.field_key}`}>
              <SelectValue />
            </SelectTrigger>
            <SelectContent>
              {STATUS_OPTIONS.map((status) => (
                <SelectItem key={status} value={status}>
                  {status === "skipped" ? "Auto-fill" : status.replace("_", " ")}
                </SelectItem>
              ))}
            </SelectContent>
          </Select>
          {row.status === "needs_review" && (
            <Button
              size="sm"
              variant="ghost"
              className="h-7 px-2 text-xs"
              disabled={disabled}
              onClick={() =>
                onPatch({
                  status: "skipped",
                  platform: platform ?? "generic",
                })
              }
            >
              Approve
            </Button>
          )}
        </div>
      </TableCell>
    </TableRow>
  );
}
