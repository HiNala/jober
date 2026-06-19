"use client";

import { useReportWebVitals } from "next/web-vitals";
import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";

import { track } from "@/lib/analytics/events";
import {
  captureUtmFromUrl,
  flushAnalytics,
  hasAnalyticsConsent,
  trackPageView,
} from "@/lib/analytics/sdk";

export function AnalyticsProvider({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();
  const initial = useRef(true);

  useEffect(() => {
    captureUtmFromUrl();
  }, [pathname]);

  useEffect(() => {
    if (!hasAnalyticsConsent()) return;
    trackPageView(pathname);
    if (initial.current) {
      initial.current = false;
    }
  }, [pathname]);

  useEffect(() => {
    const onHide = () => void flushAnalytics();
    window.addEventListener("pagehide", onHide);
    return () => window.removeEventListener("pagehide", onHide);
  }, []);

  useEffect(() => {
    if (!hasAnalyticsConsent()) return;

    const onError = (event: ErrorEvent) => {
      track("client.error", {
        message: (event.message ?? "unknown").slice(0, 200),
        path: window.location.pathname,
      });
    };

    const onUnhandledRejection = (event: PromiseRejectionEvent) => {
      const message =
        event.reason instanceof Error
          ? (event.reason.message ?? "promise rejection").slice(0, 200)
          : String(event.reason ?? "promise rejection").slice(0, 200);
      track("client.error", { message, path: window.location.pathname });
    };

    window.addEventListener("error", onError);
    window.addEventListener("unhandledrejection", onUnhandledRejection);
    return () => {
      window.removeEventListener("error", onError);
      window.removeEventListener("unhandledrejection", onUnhandledRejection);
    };
  }, []);

  useReportWebVitals(({ name, value, rating }) => {
    if (!hasAnalyticsConsent()) return;
    track("web.vital", { name, value, rating: rating ?? "unknown" });
  });

  return <>{children}</>;
}
