"use client";

import type { JobTargetRead, JobTargetStatus } from "@jober/schemas";
import { useMutation, useQueryClient } from "@tanstack/react-query";
import { FileSpreadsheet } from "lucide-react";
import Link from "next/link";
import { useEffect, useMemo, useState } from "react";
import { toast } from "sonner";

import { JobDetailDrawer } from "@/components/jobs/job-detail-drawer";
import { PageEmpty } from "@/components/states/page-states";
import { Button } from "@/components/ui/button";
import { QUEUE_EMPTY, QUEUE_FILTER_EMPTY } from "@/lib/states/onboarding-copy";
import { Badge } from "@/components/ui/badge";
import { Checkbox } from "@/components/ui/checkbox";
import { Input } from "@/components/ui/input";
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
import { updateJobTarget } from "@/lib/api/jobs";
import { JOB_STATUS_LABEL, JOB_STATUS_OPTIONS } from "@/lib/jobs/status-vocabulary";
import { cn } from "@/lib/utils";

const ATS_OPTIONS = [
  "ashby",
  "lever",
  "greenhouse",
  "workday",
  "jobvite",
  "teamtailor",
] as const;

export interface JobDataTableProps {
  rows?: JobTargetRead[];
  className?: string;
  onImportClick?: () => void;
  /** Open the detail drawer when rows load (e.g. `/queue?job=<id>`). */
  openJobId?: string | null;
}

export function JobDataTable({
  rows = [],
  className,
  onImportClick,
  openJobId = null,
}: JobDataTableProps) {
  const queryClient = useQueryClient();
  const [search, setSearch] = useState("");
  const [priority, setPriority] = useState<string>("all");
  const [status, setStatus] = useState<string>("all");
  const [ats, setAts] = useState<string>("all");
  const [location, setLocation] = useState("");
  const [selected, setSelected] = useState<Set<string>>(new Set());
  const [detail, setDetail] = useState<JobTargetRead | null>(null);

  useEffect(() => {
    if (!openJobId || rows.length === 0) return;
    const match = rows.find((row) => row.id === openJobId);
    if (match) {
      setDetail(match);
    }
  }, [openJobId, rows]);

  const filtered = useMemo(() => {
    const q = search.trim().toLowerCase();
    return rows.filter((row) => {
      if (priority !== "all" && row.priority !== priority) return false;
      if (status !== "all" && row.status !== status) return false;
      if (ats !== "all" && row.ats_guess !== ats) return false;
      const loc = location.trim().toLowerCase();
      if (loc && !(row.location_work_style ?? "").toLowerCase().includes(loc)) return false;
      if (!q) return true;
      return (
        row.company.toLowerCase().includes(q) || row.role.toLowerCase().includes(q)
      );
    });
  }, [rows, search, priority, status, ats, location]);

  const patchMutation = useMutation({
    mutationFn: ({ id, patch }: { id: string; patch: Partial<JobTargetRead> }) =>
      updateJobTarget(id, patch),
    onMutate: async ({ id, patch }) => {
      await queryClient.cancelQueries({ queryKey: ["job-targets"] });
      const previous = queryClient.getQueryData<JobTargetRead[]>(["job-targets"]);
      queryClient.setQueryData<JobTargetRead[]>(["job-targets"], (old) =>
        old?.map((row) => (row.id === id ? { ...row, ...patch } : row)),
      );
      return { previous };
    },
    onError: (_err, _vars, ctx) => {
      if (ctx?.previous) {
        queryClient.setQueryData(["job-targets"], ctx.previous);
      }
      toast.error("Could not save change");
    },
    onSettled: () => {
      void queryClient.invalidateQueries({ queryKey: ["job-targets"] });
    },
  });

  const allSelected = filtered.length > 0 && filtered.every((r) => selected.has(r.id));

  if (rows.length === 0) {
    return (
      <div className={className}>
        <PageEmpty
          title={QUEUE_EMPTY.title}
          description={QUEUE_EMPTY.description}
          icon={<FileSpreadsheet className="size-5 text-muted-foreground" aria-hidden />}
          action={
            onImportClick ? (
              <Button size="sm" onClick={onImportClick}>
                Import spreadsheet
              </Button>
            ) : undefined
          }
        />
      </div>
    );
  }

  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex flex-wrap gap-2">
        <Input
          placeholder="Search company or role…"
          className="max-w-xs"
          aria-label="Search jobs"
          value={search}
          onChange={(e) => setSearch(e.target.value)}
        />
        <Select
          value={priority}
          onValueChange={(value) => setPriority(value ?? "all")}
        >
          <SelectTrigger className="w-36" aria-label="Filter by priority">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All priorities</SelectItem>
            <SelectItem value="A">Priority A</SelectItem>
            <SelectItem value="B">Priority B</SelectItem>
            <SelectItem value="C">Priority C</SelectItem>
          </SelectContent>
        </Select>
        <Select value={status} onValueChange={(value) => setStatus(value ?? "all")}>
          <SelectTrigger className="w-40" aria-label="Filter by status">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            {JOB_STATUS_OPTIONS.map((s) => (
              <SelectItem key={s} value={s}>
                {JOB_STATUS_LABEL[s]}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Select value={ats} onValueChange={(value) => setAts(value ?? "all")}>
          <SelectTrigger className="w-36" aria-label="Filter by ATS">
            <SelectValue placeholder="ATS" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All ATS</SelectItem>
            {ATS_OPTIONS.map((platform) => (
              <SelectItem key={platform} value={platform}>
                {platform}
              </SelectItem>
            ))}
          </SelectContent>
        </Select>
        <Input
          placeholder="Location / work style"
          className="max-w-[11rem]"
          aria-label="Filter by location"
          value={location}
          onChange={(e) => setLocation(e.target.value)}
        />
      </div>
      <div className="rounded-lg border border-border/60">
        <Table className="[&_th]:bg-background [&_td]:bg-background">
          <TableHeader>
            <TableRow>
              <TableHead className="sticky left-0 z-10 w-10">
                <Checkbox
                  aria-label="Select all rows"
                  checked={allSelected}
                  onCheckedChange={(checked) => {
                    if (checked) {
                      setSelected(new Set(filtered.map((r) => r.id)));
                    } else {
                      setSelected(new Set());
                    }
                  }}
                />
              </TableHead>
              <TableHead className="sticky left-10 z-10 min-w-[7rem] shadow-[4px_0_8px_-4px_rgba(0,0,0,0.15)]">
                Company
              </TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>ATS</TableHead>
              <TableHead>Lane</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {filtered.length === 0 ? (
              <TableRow>
                <TableCell colSpan={7} className="h-24 text-center text-muted-foreground">
                  {QUEUE_FILTER_EMPTY}
                </TableCell>
              </TableRow>
            ) : (
              filtered.map((row) => (
                <TableRow
                  key={row.id}
                  data-testid="job-queue-row"
                  data-job-id={row.id}
                  className="cursor-pointer hover:bg-muted/40"
                  onClick={() => setDetail(row)}
                >
                  <TableCell className="sticky left-0 z-10" onClick={(e) => e.stopPropagation()}>
                    <Checkbox
                      aria-label={`Select ${row.company}`}
                      checked={selected.has(row.id)}
                      onCheckedChange={(checked) => {
                        setSelected((prev) => {
                          const next = new Set(prev);
                          if (checked) next.add(row.id);
                          else next.delete(row.id);
                          return next;
                        });
                      }}
                    />
                  </TableCell>
                  <TableCell className="sticky left-10 z-10 min-w-[7rem] font-medium shadow-[4px_0_8px_-4px_rgba(0,0,0,0.15)]">
                    {row.company}
                  </TableCell>
                  <TableCell>{row.role}</TableCell>
                  <TableCell>{row.priority ?? "—"}</TableCell>
                  <TableCell onClick={(e) => e.stopPropagation()}>
                    <Select
                      value={row.status}
                      onValueChange={(value) =>
                        patchMutation.mutate({
                          id: row.id,
                          patch: { status: value as JobTargetStatus },
                        })
                      }
                    >
                      <SelectTrigger className="h-8 w-[9.5rem] border-0 bg-transparent shadow-none">
                        <SelectValue />
                      </SelectTrigger>
                      <SelectContent>
                        {JOB_STATUS_OPTIONS.map((s) => (
                          <SelectItem key={s} value={s}>
                            {JOB_STATUS_LABEL[s]}
                          </SelectItem>
                        ))}
                      </SelectContent>
                    </Select>
                  </TableCell>
                  <TableCell>
                    {row.ats_guess ? (
                      <Badge variant="secondary" className="font-normal">
                        {row.ats_guess}
                      </Badge>
                    ) : row.needs_url ? (
                      <Badge variant="outline" className="font-normal text-amber-600">
                        needs URL
                      </Badge>
                    ) : (
                      "—"
                    )}
                  </TableCell>
                  <TableCell className="text-muted-foreground">
                    {row.fit_lane ?? "—"}
                  </TableCell>
                </TableRow>
              ))
            )}
          </TableBody>
        </Table>
      </div>
      {selected.size > 0 ? (
        <div className="flex flex-wrap items-center gap-3 rounded-lg border border-border/60 bg-muted/30 px-3 py-2 text-sm">
          <span className="text-muted-foreground">{selected.size} selected</span>
          <span className="text-muted-foreground">·</span>
          <span>
            Batches run from{" "}
            <Link href="/discover" className="font-medium underline underline-offset-2">
              Discover lists
            </Link>{" "}
            or the{" "}
            <Link href="/dashboard" className="font-medium underline underline-offset-2">
              dashboard
            </Link>
            .
          </span>
        </div>
      ) : null}
      <JobDetailDrawer
        job={detail}
        open={detail !== null}
        onOpenChange={(open) => !open && setDetail(null)}
        onNotesChange={(notes) => {
          if (!detail) return;
          patchMutation.mutate({ id: detail.id, patch: { notes } });
        }}
      />
    </div>
  );
}
