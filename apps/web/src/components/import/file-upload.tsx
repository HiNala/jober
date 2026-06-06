"use client";

import { FileSpreadsheet, Upload } from "lucide-react";
import { useCallback, useState } from "react";

import { cn } from "@/lib/utils";

export interface FileUploadProps {
  accept?: string;
  onFile?: (file: File) => void;
  className?: string;
}

export function FileUpload({
  accept = ".xlsx,.xls",
  onFile,
  className,
}: FileUploadProps) {
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
          <FileSpreadsheet className="size-5 text-primary" aria-hidden />
        ) : (
          <Upload className="size-5 text-muted-foreground" aria-hidden />
        )}
      </div>
      <div>
        <p className="text-sm font-medium">
          {fileName ? fileName : "Drop your job spreadsheet here"}
        </p>
        <p className="mt-1 text-xs text-muted-foreground">
          XLSX export from Direct Job Leads · or click to browse
        </p>
      </div>
    </label>
  );
}
