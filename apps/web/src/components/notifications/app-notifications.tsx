"use client";

import { useEffect, useRef } from "react";
import { toast } from "sonner";

import { useUserPreferences } from "@/contexts/user-preferences-context";
import { fetchDashboardSummary } from "@/lib/api/batches";

export function AppNotifications() {
  const { preferences } = useUserPreferences();
  const seenFinishedRef = useRef<Set<string>>(new Set());
  const initializedRef = useRef(false);

  useEffect(() => {
    if (!preferences) return;

    let cancelled = false;

    const poll = async () => {
      try {
        const summary = await fetchDashboardSummary();

        if (preferences.notifications.in_app_batch_complete) {
          for (const batch of summary.recently_finished_batches ?? []) {
            if (batch.status !== "completed" || !batch.completed_at) continue;
            const key = `${batch.id}:${batch.completed_at}`;
            if (seenFinishedRef.current.has(key)) continue;
            seenFinishedRef.current.add(key);
            if (initializedRef.current) {
              toast.success(`Batch finished: ${batch.name}`);
            }
          }
        }

        if (!initializedRef.current) {
          initializedRef.current = true;
        }
      } catch {
        // ignore transient dashboard errors
      }
    };

    void poll();
    const timer = setInterval(() => {
      if (!cancelled) void poll();
    }, 15_000);

    return () => {
      cancelled = true;
      clearInterval(timer);
    };
  }, [preferences]);

  return null;
}
