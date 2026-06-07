import { AppSidebar } from "@/components/app-shell/app-sidebar";
import { AppTopbar } from "@/components/app-shell/app-topbar";

export function AppShell({
  title,
  children,
}: {
  title: string;
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-screen bg-background">
      <a
        href="#main-content"
        className="sr-only focus:not-sr-only focus:absolute focus:left-4 focus:top-4 focus:z-50 focus:rounded-md focus:bg-primary focus:px-3 focus:py-2 focus:text-primary-foreground"
      >
        Skip to main content
      </a>
      <AppSidebar />
      <div className="flex min-h-screen flex-1 flex-col">
        <AppTopbar title={title} />
        <main className="flex-1 overflow-auto" id="main-content" tabIndex={-1}>
          {children}
        </main>
      </div>
    </div>
  );
}
