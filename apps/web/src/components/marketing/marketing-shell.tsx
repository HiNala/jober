import Link from "next/link";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { MarketingFooter } from "@/components/marketing/marketing-footer";
import { MarketingMobileNav } from "@/components/marketing/marketing-mobile-nav";
import { buttonVariants } from "@/components/ui/button";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/features", label: "Features" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/faq", label: "FAQ" },
] as const;

export function MarketingShell({
  children,
  signupFeature = "marketing_header_signup",
}: {
  children: React.ReactNode;
  signupFeature?: string;
}) {
  return (
    <div className="flex min-h-full flex-col overflow-x-clip bg-background text-foreground">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to main content
      </a>

      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-[4.25rem] max-w-6xl items-center justify-between gap-2 px-4 sm:gap-4 sm:px-6">
          <div className="flex min-w-0 items-center gap-1">
            <MarketingMobileNav />
            <Link href="/" className="truncate text-lg font-semibold tracking-tight">
              Jober
            </Link>
          </div>
          <nav
            aria-label="Marketing"
            className="hidden flex-1 items-center justify-center gap-4 lg:flex lg:gap-7"
          >
            {navLinks.map(({ href, label }) => (
              <Link
                key={href}
                href={href}
                className="text-[1.0625rem] font-medium text-muted-foreground transition-colors hover:text-foreground lg:text-[1.125rem]"
              >
                {label}
              </Link>
            ))}
          </nav>
          <div className="flex shrink-0 items-center gap-1 sm:gap-2">
            <Link
              href="/login"
              className={cn(
                buttonVariants({ variant: "ghost", size: "default" }),
                "hidden min-h-11 sm:inline-flex",
                motionPress,
              )}
            >
              Sign in
            </Link>
            <MarketingCtaLink
              href="/signup"
              feature={signupFeature}
              size="default"
              className="min-h-11"
            >
              Get started
            </MarketingCtaLink>
          </div>
        </div>
      </header>

      <main id="main-content" tabIndex={-1} className="flex-1 outline-none">
        {children}
      </main>

      <MarketingFooter />
    </div>
  );
}
