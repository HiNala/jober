import Link from "next/link";

import { MarketingHero } from "@/components/marketing/hero";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to main content
      </a>
      <header className="flex items-center justify-between px-6 py-4">
        <span className="text-sm font-semibold tracking-tight">Jober</span>
        <nav className="flex gap-4 text-sm text-muted-foreground" aria-label="Marketing">
          <Link href="/dashboard" className="hover:text-foreground">
            Dashboard
          </Link>
          <Link href="/vault" className="hover:text-foreground">
            Vault
          </Link>
        </nav>
      </header>
      <main id="main-content">
        <MarketingHero />
      </main>
      <footer className="border-t px-6 py-8 text-center text-xs text-muted-foreground">
        Assisted applications with human review before submit. You stay in control.
      </footer>
    </div>
  );
}
