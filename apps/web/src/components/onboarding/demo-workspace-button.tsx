"use client";

import { useMutation, useQueryClient } from "@tanstack/react-query";
import { Sparkles } from "lucide-react";
import { useRouter } from "next/navigation";
import { toast } from "sonner";

import { Button } from "@/components/ui/button";
import { formatApiError } from "@/lib/api/errors";
import { seedDemoWorkspace } from "@/lib/api/onboarding";

type DemoWorkspaceButtonProps = {
  variant?: "default" | "outline" | "secondary";
  size?: "default" | "sm" | "lg";
  className?: string;
  redirectTo?: string;
};

export function DemoWorkspaceButton({
  variant = "outline",
  size = "sm",
  className,
  redirectTo = "/queue",
}: DemoWorkspaceButtonProps) {
  const router = useRouter();
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: seedDemoWorkspace,
    onSuccess: async (result) => {
      await queryClient.invalidateQueries({ queryKey: ["job-targets"] });
      toast.success(`Demo workspace loaded (${result.jobs_created} sample jobs).`);
      router.push(redirectTo);
      router.refresh();
    },
    onError: (error: unknown) => {
      toast.error(formatApiError(error, "Could not load demo workspace"));
    },
  });

  return (
    <Button
      type="button"
      variant={variant}
      size={size}
      className={className}
      disabled={mutation.isPending}
      onClick={() => mutation.mutate()}
    >
      <Sparkles className="size-4" aria-hidden />
      {mutation.isPending ? "Loading demo…" : "Explore demo workspace"}
    </Button>
  );
}
