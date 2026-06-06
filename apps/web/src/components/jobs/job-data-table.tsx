"use client";

import type { JobTargetRead } from "@jober/schemas";

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
import { cn } from "@/lib/utils";

const STATUS_LABEL: Record<string, string> = {
  new: "New",
  queued: "Queued",
  in_progress: "In progress",
  applied: "Applied",
  rejected: "Rejected",
  withdrawn: "Withdrawn",
  skipped: "Skipped",
};

export interface JobDataTableProps {
  rows?: JobTargetRead[];
  className?: string;
}

export function JobDataTable({ rows = [], className }: JobDataTableProps) {
  return (
    <div className={cn("space-y-4", className)}>
      <div className="flex flex-wrap gap-2">
        <Input
          placeholder="Search company or role…"
          className="max-w-xs"
          aria-label="Search jobs"
        />
        <Select>
          <SelectTrigger className="w-36" aria-label="Filter by priority">
            <SelectValue placeholder="Priority" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All priorities</SelectItem>
            <SelectItem value="A">Priority A</SelectItem>
            <SelectItem value="B">Priority B</SelectItem>
          </SelectContent>
        </Select>
        <Select>
          <SelectTrigger className="w-36" aria-label="Filter by status">
            <SelectValue placeholder="Status" />
          </SelectTrigger>
          <SelectContent>
            <SelectItem value="all">All statuses</SelectItem>
            <SelectItem value="queued">Queued</SelectItem>
            <SelectItem value="in_progress">In progress</SelectItem>
            <SelectItem value="applied">Applied</SelectItem>
          </SelectContent>
        </Select>
      </div>
      <div className="rounded-lg border border-border/60">
        <Table>
          <TableHeader>
            <TableRow>
              <TableHead className="w-10">
                <Checkbox aria-label="Select all rows" />
              </TableHead>
              <TableHead>Company</TableHead>
              <TableHead>Role</TableHead>
              <TableHead>Priority</TableHead>
              <TableHead>Status</TableHead>
              <TableHead>Lane</TableHead>
            </TableRow>
          </TableHeader>
          <TableBody>
            {rows.length === 0 ? (
              <TableRow>
                <TableCell colSpan={6} className="h-24 text-center text-muted-foreground">
                  No job targets yet — import a spreadsheet or run{" "}
                  <code className="text-xs">make seed</code>.
                </TableCell>
              </TableRow>
            ) : (
              rows.map((row) => (
                <TableRow key={row.id} className="cursor-pointer hover:bg-muted/40">
                  <TableCell>
                    <Checkbox aria-label={`Select ${row.company}`} />
                  </TableCell>
                  <TableCell className="font-medium">{row.company}</TableCell>
                  <TableCell>{row.role}</TableCell>
                  <TableCell>{row.priority ?? "—"}</TableCell>
                  <TableCell>
                    <Badge variant="outline">{STATUS_LABEL[row.status] ?? row.status}</Badge>
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
    </div>
  );
}
