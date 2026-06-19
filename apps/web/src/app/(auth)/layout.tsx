import { AuthBrandPanel } from "@/components/auth/auth-brand-panel";
import { TrustStrip } from "@/components/marketing/trust-strip";
import { AppProviders } from "@/components/providers";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <AppProviders>
      <div className="min-h-screen lg:grid lg:h-screen lg:grid-cols-2 lg:overflow-hidden">
        {/* Brand panel — left on desktop, top strip on mobile */}
        <aside aria-label="Jober product preview" className="hidden lg:block">
          <AuthBrandPanel className="h-full" />
        </aside>
        <header className="lg:hidden">
          <AuthBrandPanel compact />
        </header>

        {/* Form panel — right on desktop */}
        <div className="flex min-h-[calc(100vh-56px)] flex-col lg:min-h-0 lg:overflow-y-auto">
          <main
            id="main-content"
            className="flex flex-1 flex-col justify-center px-8 py-10 md:px-12"
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
