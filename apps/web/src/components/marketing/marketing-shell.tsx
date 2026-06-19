"use client";

import Link from "next/link";
import { useEffect, useState } from "react";
import { usePathname } from "next/navigation";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { MarketingFooter } from "@/components/marketing/marketing-footer";
import { MarketingMobileNav } from "@/components/marketing/marketing-mobile-nav";
import { MarketingNav } from "@/components/marketing/marketing-nav";
import { buttonVariants } from "@/components/ui/button";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

/** Pages with a dark hero — nav starts transparent and gains blur on scroll. */
const DARK_HERO_ROUTES = ["/"];

export function MarketingShell({
  children,
  signupFeature = "marketing_header_signup",
}: {
  children: React.ReactNode;
  signupFeature?: string;
}) {
  const pathname = usePathname();
  const isDarkHero = DARK_HERO_ROUTES.includes(pathname);
  const [scrolled, setScrolled] = useState(false);

  useEffect(() => {
    if (!isDarkHero) return;
    function onScroll() {
      setScrolled(window.scrollY > 40);
    }
    onScroll();
    window.addEventListener("scroll", onScroll, { passive: true });
    return () => window.removeEventListener("scroll", onScroll);
  }, [isDarkHero]);

  const navScrolled = !isDarkHero || scrolled;

  return (
    <div
      className="flex min-h-full flex-col overflow-x-clip bg-background text-foreground"
      data-marketing-dark={isDarkHero ? "true" : undefined}
    >
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to main content
      </a>

      {/* Floating pill navigation — top/sides account for safe areas (notch, Dynamic Island) */}
      <div
        className="fixed inset-x-0 z-40 px-4"
        style={{ top: "max(1rem, var(--safe-top))", paddingLeft: "max(1rem, var(--safe-left))", paddingRight: "max(1rem, var(--safe-right))" }}
      >
        <header
          className={cn(
            "mx-auto flex max-w-5xl items-center justify-between gap-3 rounded-full px-4 py-2.5",
            "motion-safe:transition-[background-color,box-shadow,backdrop-filter] motion-safe:duration-[300ms] motion-safe:ease-out",
            navScrolled
              ? [
                  "bg-background/95 backdrop-blur-md",
                  "shadow-[0_2px_24px_-2px_rgba(0,0,0,0.08),0_1px_6px_-1px_rgba(0,0,0,0.04)]",
                  "ring-1 ring-black/[0.04]",
                ]
              : "bg-transparent",
          )}
        >
          <div className="flex min-w-0 items-center gap-2">
            <MarketingMobileNav />
            <Link
              href="/"
              className={cn(
                "text-base font-semibold tracking-tight motion-safe:transition-colors motion-safe:duration-200",
                isDarkHero && !scrolled ? "text-white" : "text-foreground",
              )}
            >
              Jober
            </Link>
          </div>

          <MarketingNav dark={isDarkHero && !scrolled} />

          <div className="flex shrink-0 items-center gap-1">
            <Link
              href="/login"
              className={cn(
                buttonVariants({ variant: "ghost", size: "sm" }),
                "hidden sm:inline-flex",
                motionPress,
                isDarkHero && !scrolled && "text-white/80 hover:bg-white/10 hover:text-white",
              )}
            >
              Sign in
            </Link>
            <MarketingCtaLink
              href="/signup"
              feature={signupFeature}
              size="sm"
              variant={isDarkHero && !scrolled ? "ghost" : "default"}
              className={cn(
                "rounded-full",
                isDarkHero && !scrolled &&
                  "bg-[oklch(0.78_0.14_68)] text-[#0a0908] hover:bg-[oklch(0.72_0.14_68)] hover:text-[#0a0908]",
              )}
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
