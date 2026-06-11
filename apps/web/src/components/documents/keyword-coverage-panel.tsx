"use client";

import { HelpCircle } from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { Card, CardContent, CardHeader, CardTitle } from "@/components/ui/card";
import { Progress } from "@/components/ui/progress";
import {
  Tooltip,
  TooltipContent,
  TooltipProvider,
  TooltipTrigger,
} from "@/components/ui/tooltip";
import { surface } from "@/lib/design/tokens";
import type { KeywordCoverage } from "@/lib/api/documents";
import { cn } from "@/lib/utils";

const COVERAGE_HELP =
  "Keyword coverage compares job-description terms to your letter. Present terms help ATS parsers; missing terms are suggestions, not requirements.";

export function KeywordCoveragePanel({
  atsScore,
  coverage,
  className,
}: {
  atsScore: number;
  coverage?: KeywordCoverage | null;
  className?: string;
}) {
  return (
    <TooltipProvider>
      <div className={cn("grid gap-4 sm:grid-cols-2", className)}>
        <Card className={surface.workspace}>
          <CardHeader className="pb-2">
            <CardTitle className="text-sm">ATS score</CardTitle>
          </CardHeader>
          <CardContent className="space-y-2">
            <div className="flex items-center gap-3">
              <Progress value={atsScore} className="flex-1" aria-label="ATS keyword score" />
              <span className="text-sm font-medium tabular-nums">{atsScore}</span>
            </div>
            {coverage && coverage.stuffing_penalty > 0 ? (
              <p className="text-xs text-amber-600">
                Stuffing penalty −{coverage.stuffing_penalty} (density {coverage.density})
              </p>
            ) : null}
          </CardContent>
        </Card>
        <Card className={surface.workspace}>
          <CardHeader className="flex flex-row items-center gap-2 pb-2">
            <CardTitle className="text-sm">Keyword coverage</CardTitle>
            <Tooltip>
              <TooltipTrigger
                type="button"
                className="text-muted-foreground hover:text-foreground"
                aria-label="What keyword coverage measures"
              >
                <HelpCircle className="size-3.5" aria-hidden />
              </TooltipTrigger>
              <TooltipContent className="max-w-xs text-xs">{COVERAGE_HELP}</TooltipContent>
            </Tooltip>
          </CardHeader>
          <CardContent className="flex flex-wrap gap-1">
            {coverage?.present.map((kw) => (
              <Badge key={kw} variant="secondary" className="font-normal">
                {kw}
              </Badge>
            ))}
            {coverage?.missing.map((kw) => (
              <Badge key={kw} variant="outline" className="font-normal text-muted-foreground">
                missing: {kw}
              </Badge>
            ))}
            {!coverage?.present.length && !coverage?.missing.length ? (
              <p className="text-xs text-muted-foreground">Generate a letter to see coverage.</p>
            ) : null}
          </CardContent>
        </Card>
      </div>
    </TooltipProvider>
  );
}
