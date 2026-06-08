"use client";

import { Eye, EyeOff } from "lucide-react";
import { useMemo, useState } from "react";

import { Button } from "@/components/ui/button";
import { Input } from "@/components/ui/input";
import { motionMicro } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

function scorePassword(value: string): number {
  let score = 0;
  if (value.length >= 10) score += 1;
  if (value.length >= 14) score += 1;
  if (/[a-z]/.test(value) && /[A-Z]/.test(value)) score += 1;
  if (/\d/.test(value)) score += 1;
  if (/[^A-Za-z0-9]/.test(value)) score += 1;
  return Math.min(score, 4);
}

const LABELS = ["Weak", "Fair", "Good", "Strong"] as const;

export function PasswordField({
  id,
  value,
  onChange,
  label = "Password",
  showMeter = true,
  autoComplete,
}: {
  id: string;
  value: string;
  onChange: (value: string) => void;
  label?: string;
  showMeter?: boolean;
  autoComplete?: string;
}) {
  const [visible, setVisible] = useState(false);
  const score = useMemo(() => scorePassword(value), [value]);

  return (
    <div className="space-y-2">
      <label htmlFor={id} className="text-sm font-medium">
        {label}
      </label>
      <div className="relative">
        <Input
          id={id}
          type={visible ? "text" : "password"}
          value={value}
          onChange={(e) => onChange(e.target.value)}
          autoComplete={autoComplete}
          className="pr-10"
          minLength={10}
          required
        />
        <Button
          type="button"
          variant="ghost"
          size="icon-sm"
          className={cn("absolute right-1 top-1/2 -translate-y-1/2", motionMicro)}
          onClick={() => setVisible((v) => !v)}
          aria-label={visible ? "Hide password" : "Show password"}
        >
          {visible ? <EyeOff className="size-4" /> : <Eye className="size-4" />}
        </Button>
      </div>
      {showMeter && value.length > 0 ? (
        <div className="space-y-1" aria-live="polite">
          <div className="flex gap-1">
            {Array.from({ length: 4 }).map((_, index) => (
              <div
                key={index}
                className={cn(
                  "h-1 flex-1 rounded-full",
                  index < score ? "bg-primary" : "bg-muted",
                )}
              />
            ))}
          </div>
          <p className="text-xs text-muted-foreground">
            Strength: {LABELS[Math.max(0, score - 1)] ?? "Weak"}
          </p>
        </div>
      ) : null}
    </div>
  );
}
