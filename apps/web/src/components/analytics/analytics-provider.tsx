"use client";

import { usePathname } from "next/navigation";
import { useEffect, useRef } from "react";

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

  return <>{children}</>;
}
