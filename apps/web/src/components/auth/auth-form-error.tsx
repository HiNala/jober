import { AlertCircle } from "lucide-react";

import { cn } from "@/lib/utils";

export function AuthFormError({ message, className }: { message: string; className?: string }) {
  return (
    <div
      className={cn(
        "flex gap-2 rounded-md border border-destructive/30 bg-destructive/5 px-3 py-2 text-sm text-destructive",
        className,
      )}
      role="alert"
    >
      <AlertCircle className="mt-0.5 size-4 shrink-0" aria-hidden />
      <p>{message}</p>
    </div>
  );
}
