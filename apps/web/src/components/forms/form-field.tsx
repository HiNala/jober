import type { ReactNode } from "react";

import { cn } from "@/lib/utils";

export function FormField({
  id,
  label,
  error,
  children,
  className,
}: {
  id: string;
  label: string;
  error?: string | null;
  children: ReactNode;
  className?: string;
}) {
  const errorId = error ? `${id}-error` : undefined;
  return (
    <div className={cn("space-y-2", className)}>
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      {children}
      {error ? (
        <p id={errorId} className="text-sm text-destructive" role="alert">
          {error}
        </p>
      ) : null}
    </div>
  );
}

export function fieldDescribedBy(error?: string | null, id?: string): string | undefined {
  if (!error || !id) return undefined;
  return `${id}-error`;
}
