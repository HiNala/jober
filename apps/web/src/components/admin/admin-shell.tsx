"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { AdminRouteGuard } from "@/components/auth/admin-route-guard";
import { cn } from "@/lib/utils";
import {
  Activity,
  Flag,
  LayoutDashboard,
  LineChart,
  Server,
  Shield,
  Users,
  Workflow,
  type LucideIcon,
} from "lucide-react";

const ADMIN_SECTIONS: { href: string; label: string; icon: LucideIcon }[] = [
  { href: "/admin", label: "Overview", icon: LayoutDashboard },
  { href: "/admin/acquisition", label: "Acquisition", icon: LineChart },
  { href: "/admin/users", label: "Users", icon: Users },
  { href: "/admin/runs", label: "Runs", icon: Workflow },
  { href: "/admin/cost", label: "Cost", icon: Activity },
  { href: "/admin/system", label: "System", icon: Server },
  { href: "/admin/config", label: "Config", icon: Flag },
];

export function AdminShell({ children }: { children: React.ReactNode }) {
  const pathname = usePathname();

  return (
    <AdminRouteGuard>
      <div className="flex flex-col gap-6 lg:flex-row lg:items-start">
        <nav
          aria-label="Admin sections"
          className="flex shrink-0 flex-wrap gap-1 lg:w-44 lg:flex-col"
        >
          <div className="mb-2 hidden items-center gap-2 px-2 text-xs font-medium uppercase tracking-wide text-muted-foreground lg:flex">
            <Shield className="size-3.5" aria-hidden />
            Admin
          </div>
          {ADMIN_SECTIONS.map(({ href, label, icon: Icon }) => {
            const active =
              href === "/admin"
                ? pathname === "/admin"
                : pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                key={href}
                href={href}
                className={cn(
                  "flex items-center gap-2 rounded-md px-2.5 py-2 text-sm transition-colors",
                  active
                    ? "bg-primary text-primary-foreground"
                    : "text-muted-foreground hover:bg-muted hover:text-foreground",
                )}
                aria-current={active ? "page" : undefined}
              >
                <Icon className="size-4 shrink-0" aria-hidden />
                {label}
              </Link>
            );
          })}
        </nav>
        <div className="min-w-0 flex-1">{children}</div>
      </div>
    </AdminRouteGuard>
  );
}
