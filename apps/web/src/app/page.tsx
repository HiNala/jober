import Link from "next/link";

import { MarketingHero } from "@/components/marketing/hero";

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-background">
      <header className="flex items-center justify-between px-6 py-4">
        <span className="text-sm font-semibold tracking-tight">Jober</span>
        <nav className="flex gap-4 text-sm text-muted-foreground">
          <Link href="/dashboard" className="hover:text-foreground">
            Dashboard
          </Link>
          <Link href="/kitchen-sink" className="hover:text-foreground">
            Kitchen sink
          </Link>
        </nav>
      </header>
      <main>
        <MarketingHero />
      </main>
      <footer className="border-t px-6 py-8 text-center text-xs text-muted-foreground">
        Assisted applications with human review before submit.
      </footer>
    </div>
  );
}
