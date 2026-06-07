"use client";

import { useCallback, useEffect, useRef, useState } from "react";

import {
  fetchRunConsoleSnapshot,
  runEventsStreamUrl,
  type RunConsoleSnapshot,
  type RunStreamEvent,
} from "@/lib/api/run-console";

export type RunStreamStatus = "idle" | "connecting" | "open" | "closed" | "error";

export function useRunStream(runId: string | null) {
  const [status, setStatus] = useState<RunStreamStatus>(runId ? "connecting" : "idle");
  const [events, setEvents] = useState<RunStreamEvent[]>([]);
  const [snapshot, setSnapshot] = useState<RunConsoleSnapshot | null>(null);
  const [lastSeq, setLastSeq] = useState(0);
  const [selectedTimelineSeq, setSelectedTimelineSeq] = useState<number | null>(null);
  const lastSeqRef = useRef(0);
  const sourceRef = useRef<EventSource | null>(null);

  const mergeEvents = useCallback((incoming: RunStreamEvent[]) => {
    if (incoming.length === 0) {
      return;
    }
    setEvents((prev) => {
      const bySeq = new Map(prev.map((event) => [event.seq, event]));
      for (const event of incoming) {
        bySeq.set(event.seq, event);
      }
      return [...bySeq.values()].sort((a, b) => a.seq - b.seq);
    });
    const maxSeq = Math.max(...incoming.map((event) => event.seq));
    if (maxSeq > lastSeqRef.current) {
      lastSeqRef.current = maxSeq;
      setLastSeq(maxSeq);
    }
  }, []);

  const openStream = useCallback((id: string, afterSeq: number) => {
    sourceRef.current?.close();
    const source = new EventSource(runEventsStreamUrl(id, afterSeq));
    sourceRef.current = source;
    source.onopen = () => setStatus("open");
    source.onerror = () => setStatus("error");
    source.onmessage = (message) => {
      try {
        const parsed = JSON.parse(message.data) as RunStreamEvent;
        mergeEvents([parsed]);
        setSnapshot((prev) =>
          prev
            ? {
                ...prev,
                last_event_seq: parsed.seq,
                latest_screenshot_url: parsed.screenshot_url ?? prev.latest_screenshot_url,
                status:
                  parsed.event_type === "state.changed"
                    ? String(parsed.payload?.status ?? prev.status)
                    : prev.status,
              }
            : prev,
        );
      } catch {
        // ignore malformed chunks
      }
    };
  }, [mergeEvents]);

  const reconnect = useCallback(async () => {
    if (!runId) {
      return;
    }
    setStatus("connecting");
    try {
      const initial = await fetchRunConsoleSnapshot(runId);
      setSnapshot(initial);
      mergeEvents(initial.events);
      lastSeqRef.current = initial.last_event_seq;
      setLastSeq(initial.last_event_seq);
      openStream(runId, lastSeqRef.current);
    } catch {
      setStatus("error");
    }
  }, [mergeEvents, openStream, runId]);

  useEffect(() => {
    if (!runId) {
      return;
    }
    let cancelled = false;

    const bootstrap = async () => {
      setStatus("connecting");
      try {
        const initial = await fetchRunConsoleSnapshot(runId);
        if (cancelled) {
          return;
        }
        setSnapshot(initial);
        mergeEvents(initial.events);
        lastSeqRef.current = initial.last_event_seq;
        setLastSeq(initial.last_event_seq);
        openStream(runId, lastSeqRef.current);
      } catch {
        if (!cancelled) {
          setStatus("error");
        }
      }
    };

    void bootstrap();

    return () => {
      cancelled = true;
      sourceRef.current?.close();
      setStatus("closed");
    };
  }, [mergeEvents, openStream, runId]);

  const scrubScreenshotUrl =
    selectedTimelineSeq !== null
      ? snapshot?.timeline.find((item) => item.seq === selectedTimelineSeq)?.screenshot_url
      : null;

  return {
    status: runId ? status : "idle",
    events: runId ? events : [],
    snapshot: runId ? snapshot : null,
    lastSeq,
    reconnect,
    selectedTimelineSeq,
    setSelectedTimelineSeq,
    scrubScreenshotUrl,
    displayScreenshotUrl:
      scrubScreenshotUrl ?? snapshot?.latest_screenshot_url ?? null,
  };
}
