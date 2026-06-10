"use client";

import { useCallback, useEffect, useMemo, useRef, useState } from "react";

import {
  fetchRunConsoleSnapshot,
  runEventsStreamUrl,
  type RunConsoleSnapshot,
  type RunStreamEvent,
} from "@/lib/api/run-console";
import { applyStreamEvent } from "@/lib/run-stream/apply-stream-event";
import { RUN_SSE_EVENT_TYPES } from "@/lib/run-stream/event-types";

export type RunStreamStatus = "idle" | "connecting" | "open" | "closed" | "error";

export function useRunStream(runId: string | null) {
  const [status, setStatus] = useState<RunStreamStatus>(runId ? "connecting" : "idle");
  const [events, setEvents] = useState<RunStreamEvent[]>([]);
  const [snapshot, setSnapshot] = useState<RunConsoleSnapshot | null>(null);
  const [lastSeq, setLastSeq] = useState(0);
  const [selectedTimelineSeq, setSelectedTimelineSeq] = useState<number | null>(null);
  const [liveFollow, setLiveFollow] = useState(true);
  const liveFollowRef = useRef(liveFollow);
  const lastSeqRef = useRef(0);
  const sourceRef = useRef<EventSource | null>(null);
  const reconnectTimerRef = useRef<ReturnType<typeof setTimeout> | null>(null);
  const reconnectRef = useRef<() => Promise<void>>(async () => {});

  useEffect(() => {
    liveFollowRef.current = liveFollow;
  }, [liveFollow]);

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

  const handleStreamPayload = useCallback(
    (raw: string) => {
      try {
        const parsed = JSON.parse(raw) as RunStreamEvent;
        mergeEvents([parsed]);
        setSnapshot((prev) => applyStreamEvent(prev, parsed));
        if (liveFollowRef.current && parsed.screenshot_url) {
          setSelectedTimelineSeq(null);
        }
      } catch {
        // ignore malformed chunks
      }
    },
    [mergeEvents],
  );

  const openStream = useCallback(
    (id: string, afterSeq: number) => {
      sourceRef.current?.close();
      const source = new EventSource(runEventsStreamUrl(id, afterSeq));
      sourceRef.current = source;
      source.onopen = () => setStatus("open");
      source.onerror = () => {
        setStatus("error");
        source.close();
        if (reconnectTimerRef.current) {
          clearTimeout(reconnectTimerRef.current);
        }
        reconnectTimerRef.current = setTimeout(() => {
          reconnectTimerRef.current = null;
          void reconnectRef.current();
        }, 3000);
      };
      source.onmessage = (message) => handleStreamPayload(message.data);
      for (const eventType of RUN_SSE_EVENT_TYPES) {
        source.addEventListener(eventType, (message) => {
          const event = message as MessageEvent<string>;
          handleStreamPayload(event.data);
        });
      }
    },
    [handleStreamPayload],
  );

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
    reconnectRef.current = reconnect;
  }, [reconnect]);

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
      if (reconnectTimerRef.current) {
        clearTimeout(reconnectTimerRef.current);
        reconnectTimerRef.current = null;
      }
      sourceRef.current?.close();
      setStatus("closed");
    };
  }, [mergeEvents, openStream, runId]);

  const scrubToTimeline = useCallback((seq: number | null) => {
    setSelectedTimelineSeq(seq);
    setLiveFollow(seq === null);
  }, []);

  const catchUpToLive = useCallback(() => {
    setSelectedTimelineSeq(null);
    setLiveFollow(true);
  }, []);

  const scrubScreenshotUrl =
    selectedTimelineSeq !== null
      ? snapshot?.timeline.find((item) => item.seq === selectedTimelineSeq)?.screenshot_url ??
        events.find((event) => event.seq === selectedTimelineSeq)?.screenshot_url ??
        null
      : null;

  const latestBrowserContext = useMemo(() => {
    let url: string | null = null;
    let action: string | null = null;
    const relevant = [...events].reverse();
    for (const event of relevant) {
      if (!action && event.event_type === "browser.action") {
        action = event.message;
      }
      if (!url && event.event_type === "browser.navigated") {
        url = String(event.payload?.url ?? event.message);
      }
      if (url && action) {
        break;
      }
    }
    return { url, action };
  }, [events]);

  const warningCount = useMemo(
    () =>
      events.filter(
        (event) =>
          event.event_type === "verification.warning" || event.event_type === "human.required",
      ).length,
    [events],
  );

  return {
    status: runId ? status : "idle",
    events: runId ? events : [],
    snapshot: runId ? snapshot : null,
    lastSeq,
    reconnect,
    selectedTimelineSeq,
    setSelectedTimelineSeq: scrubToTimeline,
    liveFollow,
    catchUpToLive,
    scrubScreenshotUrl,
    displayScreenshotUrl:
      scrubScreenshotUrl ?? snapshot?.latest_screenshot_url ?? null,
    latestUrl: latestBrowserContext.url,
    latestAction: latestBrowserContext.action,
    warningCount,
    isReviewState:
      snapshot?.status === "review_and_submit" ||
      snapshot?.open_checkpoint?.checkpoint_type === "review_submit",
  };
}
