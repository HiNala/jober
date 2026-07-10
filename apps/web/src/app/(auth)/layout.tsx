import { AuthBrandPanel } from "@/components/auth/auth-brand-panel";
import { TrustStrip } from "@/components/marketing/trust-strip";
import { AppProviders } from "@/components/providers";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppProviders>
      <div className="min-h-screen bg-background text-foreground lg:grid lg:h-screen lg:grid-cols-2 lg:overflow-hidden">
        {/* Brand panel — left on desktop, top strip on mobile */}
        <aside aria-label="Jober product preview" className="hidden lg:block">
          <AuthBrandPanel className="h-full" />
        </aside>
        <header className="border-border/40 bg-background lg:hidden">
          <AuthBrandPanel compact />
        </header>

        {/* Form panel — right on desktop; dark tokens + subtle ambient */}
        <div className="relative flex min-h-[calc(100vh-56px)] flex-col bg-background lg:min-h-0 lg:overflow-y-auto">
          <div aria-hidden className="pointer-events-none absolute inset-0 overflow-hidden">
            <div className="absolute -right-24 top-0 size-[420px] rounded-full bg-primary/15 opacity-80 blur-3xl" />
            <div className="absolute -bottom-32 -left-16 size-[360px] rounded-full bg-accent/10 opacity-80 blur-3xl" />
          </div>
          <main
            id="main-content"
            className="relative flex flex-1 flex-col justify-center px-8 py-10 md:px-12"
            style={{
              paddingLeft: "max(2rem, var(--safe-left))",
              paddingRight: "max(2rem, var(--safe-right))",
              paddingBottom: "max(2.5rem, var(--safe-bottom))",
            }}
            tabIndex={-1}
          >
            <div className="mx-auto w-full max-w-sm">{children}</div>
            <TrustStrip className="mx-auto mt-8 max-w-sm" />
          </main>
        </div>
      </div>
    </AppProviders>
  );
}
