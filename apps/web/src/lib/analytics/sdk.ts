import { getApiBaseUrl } from "@/lib/api/client";

const CONSENT_COOKIE = "jober_analytics_consent";
const ANON_KEY = "jober_anon_id";
const ANON_ROTATED_KEY = "jober_anon_rotated_at";
const SESSION_KEY = "jober_analytics_session";
const ROTATION_DAYS = 30;

type AnalyticsEventPayload = {
  name: string;
  ts?: string;
  anon_id?: string;
  session_id: string;
  page?: string;
  referrer?: string;
  utm_source?: string;
  utm_medium?: string;
  utm_campaign?: string;
  utm_term?: string;
  utm_content?: string;
  props?: Record<string, string | number | boolean | null>;
};

let queue: AnalyticsEventPayload[] = [];
let flushTimer: ReturnType<typeof setTimeout> | null = null;

export function isDoNotTrackEnabled(): boolean {
  if (typeof navigator === "undefined") return false;
  const dnt = navigator.doNotTrack;
  return dnt === "1" || dnt === "yes";
}

export function hasAnalyticsConsent(): boolean {
  if (typeof document === "undefined") return false;
  if (isDoNotTrackEnabled()) return false;
  const match = document.cookie.match(new RegExp(`(?:^|;\\s*)${CONSENT_COOKIE}=([^;]+)`));
  return match?.[1] === "1";
}

export function setAnalyticsConsent(accepted: boolean): void {
  if (typeof document === "undefined") return;
  const maxAge = accepted ? 60 * 60 * 24 * 365 : 60 * 60 * 24 * 30;
  document.cookie = `${CONSENT_COOKIE}=${accepted ? "1" : "0"}; path=/; max-age=${maxAge}; SameSite=Lax`;
}

function readUtmParams(): Pick<
  AnalyticsEventPayload,
  "utm_source" | "utm_medium" | "utm_campaign" | "utm_term" | "utm_content"
> {
  if (typeof window === "undefined") return {};
  const params = new URLSearchParams(window.location.search);
  return {
    utm_source: params.get("utm_source") ?? undefined,
    utm_medium: params.get("utm_medium") ?? undefined,
    utm_campaign: params.get("utm_campaign") ?? undefined,
    utm_term: params.get("utm_term") ?? undefined,
    utm_content: params.get("utm_content") ?? undefined,
  };
}

function rotateAnonIdIfNeeded(): string {
  const now = Date.now();
  const rotatedAt = Number(localStorage.getItem(ANON_ROTATED_KEY) ?? "0");
  let anonId = localStorage.getItem(ANON_KEY);
  const rotationMs = ROTATION_DAYS * 24 * 60 * 60 * 1000;
  if (!anonId || now - rotatedAt > rotationMs) {
    anonId = crypto.randomUUID();
    localStorage.setItem(ANON_KEY, anonId);
    localStorage.setItem(ANON_ROTATED_KEY, String(now));
  }
  return anonId;
}

function analyticsSessionId(): string {
  let sessionId = sessionStorage.getItem(SESSION_KEY);
  if (!sessionId) {
    sessionId = crypto.randomUUID();
    sessionStorage.setItem(SESSION_KEY, sessionId);
  }
  return sessionId;
}

function enqueue(event: AnalyticsEventPayload): void {
  queue.push(event);
  if (flushTimer) return;
  flushTimer = setTimeout(() => {
    flushTimer = null;
    void flushAnalytics();
  }, 1500);
}

export function trackEvent(
  name: string,
  props?: Record<string, string | number | boolean | null>,
): void {
  if (!hasAnalyticsConsent()) return;
  const payload: AnalyticsEventPayload = {
    name,
    ts: new Date().toISOString(),
    anon_id: rotateAnonIdIfNeeded(),
    session_id: analyticsSessionId(),
    page: typeof window !== "undefined" ? window.location.pathname : undefined,
    referrer: typeof document !== "undefined" ? document.referrer || undefined : undefined,
    ...readUtmParams(),
    props,
  };
  enqueue(payload);
}

export function trackPageView(path?: string, title?: string): void {
  trackEvent("page.view", {
    path: path ?? (typeof window !== "undefined" ? window.location.pathname : "/"),
    title: title ?? (typeof document !== "undefined" ? document.title : ""),
  });
}

export async function flushAnalytics(): Promise<void> {
  if (!hasAnalyticsConsent() || queue.length === 0) return;
  const batch = queue.splice(0, 50);
  const body = JSON.stringify({ events: batch });
  const url = `${getApiBaseUrl()}/api/events`;

  try {
    if (typeof navigator !== "undefined" && navigator.sendBeacon) {
      const blob = new Blob([body], { type: "application/json" });
      if (navigator.sendBeacon(url, blob)) return;
    }
    await fetch(url, {
      method: "POST",
      credentials: "include",
      headers: { "Content-Type": "application/json", Accept: "application/json" },
      body,
      keepalive: true,
    });
  } catch {
    // Fail silently — analytics must never block the UI.
  }
}
