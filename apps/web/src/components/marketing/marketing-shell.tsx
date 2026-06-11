import Link from "next/link";

import { MarketingCtaLink } from "@/components/marketing/marketing-cta-link";
import { MarketingFooter } from "@/components/marketing/marketing-footer";
import { buttonVariants } from "@/components/ui/button";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/features", label: "Features", mobile: true },
  { href: "/how-it-works", label: "How it works", mobile: false },
  { href: "/pricing", label: "Pricing", mobile: true },
  { href: "/faq", label: "FAQ", mobile: false },
] as const;

export function MarketingShell({
  children,
  signupFeature = "marketing_header_signup",
}: {
  children: React.ReactNode;
  signupFeature?: string;
}) {
  return (
    <div className="flex min-h-full flex-col bg-background text-foreground">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to main content
      </a>

      <header className="sticky top-0 z-40 border-b border-border/60 bg-background/80 backdrop-blur-md">
        <div className="mx-auto flex h-16 max-w-6xl items-center justify-between gap-4 px-6">
          <Link href="/" className="text-base font-semibold tracking-tight">
            Jober
          </Link>
          <nav aria-label="Marketing" className="flex items-center gap-4 md:gap-6">
            {navLinks.map(({ href, label, mobile }) => (
              <Link
                key={href}
                href={href}
                className={cn(
                  "text-base font-medium text-muted-foreground transition-colors hover:text-foreground",
                  !mobile && "hidden md:inline",
                )}
              >
                {label}
              </Link>
            ))}
          </nav>
          <div className="flex items-center gap-2">
            <Link
              href="/login"
              className={cn(buttonVariants({ variant: "ghost", size: "default" }), motionPress)}
            >
              Sign in
            </Link>
            <MarketingCtaLink href="/signup" feature={signupFeature} size="default">
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
