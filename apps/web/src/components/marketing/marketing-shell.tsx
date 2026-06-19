"use client";

import Link from "next/link";
import { useEffect, useState } from "react";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { MarketingFooter } from "@/components/marketing/marketing-footer";
import { MarketingMobileNav } from "@/components/marketing/marketing-mobile-nav";
import { MarketingNav } from "@/components/marketing/marketing-nav";
import { buttonVariants } from "@/components/ui/button";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

export function MarketingShell({
  children,
  signupFeature = "marketing_header_signup",
}: {
  children: React.ReactNode;
  signupFeature?: string;
}) {
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    function onScroll() {
      setScrolled(window.scrollY > 40);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, []);

  return (
    <div className="flex min-h-full flex-col overflow-x-clip bg-background text-foreground">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to main content
      </a>

      {/* Fixed floating navigation */}
      <div
        className="fixed inset-x-0 z-40 px-4"
        style={{ top: "max(1rem, var(--safe-top))", paddingLeft: "max(1rem, var(--safe-left))", paddingRight: "max(1rem, var(--safe-right))" }}
      >
        <header
          className={cn(
            "mx-auto flex max-w-5xl items-center justify-between gap-3 rounded-full px-4 py-2.5",
            "bg-white/95 backdrop-blur-md",
            "motion-safe:transition-[box-shadow] motion-safe:duration-[300ms] motion-safe:ease-out",
            scrolled
              ? "shadow-[0_2px_24px_-2px_rgba(0,0,0,0.10),0_1px_6px_-1px_rgba(0,0,0,0.05)] ring-1 ring-black/[0.05]"
              : "shadow-sm ring-1 ring-black/[0.04]",
          )}
        >
          <div className="flex min-w-0 items-center gap-2">
            <MarketingMobileNav />
            <Link
              href="/"
              className="text-base font-semibold tracking-tight text-foreground motion-safe:transition-colors motion-safe:duration-200"
            >
              Jober
            </Link>
          </div>

          <MarketingNav />

          <div className="flex shrink-0 items-center gap-1">
            <Link
              href="/login"
              className={cn(
                buttonVariants({ variant: "ghost", size: "sm" }),
                "hidden sm:inline-flex",
                motionPress,
              )}
            >
              Sign in
            </Link>
            <MarketingCtaLink
              href="/signup"
              feature={signupFeature}
              size="sm"
              variant="default"
              className="rounded-full"
            >
              Get started
            </MarketingCtaLink>
          </div>
        </header>
      </div>

      {/* Offset content so it clears the fixed nav (80px + safe area top) */}
      <main
        id="main-content"
        tabIndex={-1}
        className="flex-1 outline-none"
        style={{ paddingTop: "calc(5rem + var(--safe-top))" }}
      >
        {children}
      </main>

      <MarketingFooter />
    </div>
  );
}
