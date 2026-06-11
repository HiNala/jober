"use client";

import { FileSpreadsheet, FileText, Upload } from "lucide-react";
import { useCallback, useState } from "react";

import { cn } from "@/lib/utils";

export type FileUploadKind = "spreadsheet" | "resume";

const UPLOAD_COPY: Record<
  FileUploadKind,
  { title: string; hint: string; Icon: typeof Upload }
> = {
  spreadsheet: {
    title: "Drop your job spreadsheet here",
    hint: "XLSX export from your tracker · or click to browse",
    Icon: FileSpreadsheet,
  },
  resume: {
    title: "Drop your resume here",
    hint: "PDF or DOCX · parsed skills feed generation and claims checks",
    Icon: FileText,
  },
};

export interface FileUploadProps {
  accept?: string;
  kind?: FileUploadKind;
  title?: string;
  hint?: string;
  onFile?: (file: File) => void;
  className?: string;
}

export function FileUpload({
  accept = ".xlsx,.xls",
  kind = "spreadsheet",
  title,
  hint,
  onFile,
  className,
}: FileUploadProps) {
  const defaults = UPLOAD_COPY[kind];
  const displayTitle = title ?? defaults.title;
  const displayHint = hint ?? defaults.hint;
  const DoneIcon = defaults.Icon;
  const [dragOver, setDragOver] = useState(false);
  const [fileName, setFileName] = useState<string | null>(null);

  const handleFiles = useCallback(
    (files: FileList | null) => {
      const file = files?.[0];
      if (!file) return;
      setFileName(file.name);
      onFile?.(file);
    },
    [onFile],
  );

  return (
    <label
      className={cn(
        "flex cursor-pointer flex-col items-center justify-center gap-3 rounded-lg border-2 border-dashed px-6 py-12 text-center transition-colors",
        "focus-within:ring-2 focus-within:ring-ring focus-within:ring-offset-2 focus-within:ring-offset-background",
        dragOver
          ? "border-primary bg-primary/5"
          : "border-border/80 bg-muted/20 hover:border-primary/50 hover:bg-muted/30",
        className,
      )}
      onDragOver={(e) => {
        e.preventDefault();
        setDragOver(true);
      }}
      onDragLeave={() => setDragOver(false)}
      onDrop={(e) => {
        e.preventDefault();
        setDragOver(false);
        handleFiles(e.dataTransfer.files);
      }}
    >
      <input
        type="file"
        accept={accept}
        className="sr-only"
        onChange={(e) => handleFiles(e.target.files)}
      />
      <div className="flex size-12 items-center justify-center rounded-full bg-muted">
        {fileName ? (
          <DoneIcon className="size-5 text-primary" aria-hidden />
        ) : (
          <Upload className="size-5 text-muted-foreground" aria-hidden />
        )}
      </div>
      <div>
        <p className="text-sm font-medium">{fileName ? fileName : displayTitle}</p>
        {!fileName ? (
          <p className="mt-1 text-xs text-muted-foreground">{displayHint}</p>
        ) : null}
      </div>
    </label>
  );
}
