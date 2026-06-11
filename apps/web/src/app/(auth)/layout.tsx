import { AuthBrandPanel } from "@/components/auth/auth-brand-panel";
import { TrustStrip } from "@/components/marketing/trust-strip";

export default function AuthLayout({ children }: { children: React.ReactNode }) {
  return (
    <div className="min-h-screen lg:grid lg:grid-cols-2">
      <aside aria-label="Jober product preview" className="hidden min-h-screen lg:block">
        <AuthBrandPanel className="h-full" />
      </aside>
      <div className="flex min-h-screen flex-col">
        <header className="lg:hidden">
          <AuthBrandPanel compact />
        </header>
        <main
          id="main-content"
          className="flex flex-1 flex-col justify-center px-6 py-8"
          tabIndex={-1}
        >
          <div className="mx-auto w-full max-w-md">{children}</div>
          <TrustStrip className="mx-auto mt-8 max-w-md" />
        </main>
      </div>
    </div>
  );
}
