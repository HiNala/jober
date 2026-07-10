"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/contexts/auth-context";
import { isAdmin } from "@/lib/auth/permissions";
import {
  BarChart3,
  BookOpen,
  Compass,
  FileText,
  LayoutDashboard,
  ListTodo,
  Search,
  Settings,
  Shield,
  LockKeyhole,
  type LucideIcon,
} from "lucide-react";

import { Badge } from "@/components/ui/badge";
import { cn } from "@/lib/utils";

export type NavItem = {
  href: string;
  label: string;
  description?: string;
  icon: LucideIcon;
};

/** Flat list used by mobile sheets / tests. */
export const APP_NAV: NavItem[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/queue", label: "Queue", icon: ListTodo, description: "Your job tracker table" },
  {
    href: "/discover",
    label: "Discover",
    icon: Compass,
    description: "Find new jobs — boards or spreadsheet",
  },
  {
    href: "/documents",
    label: "Documents",
    icon: FileText,
    description: "Tailor cover letters and resume variants",
  },
  { href: "/library", label: "Library", icon: BookOpen },
  {
    href: "/vault",
    label: "Vault",
    icon: LockKeyhole,
    description: "Profile, resume, and autofill data",
  },
  {
    href: "/search",
    label: "Search",
    icon: Search,
    description: "Search jobs, letters, and runs you already have",
  },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

/** Hyperagent-style grouped rail — Work / Materials / Insights. */
const NAV_SECTIONS: { id: string; label: string; items: NavItem[] }[] = [
  {
    id: "work",
    label: "Work",
    items: [
      APP_NAV[0], // dashboard
      APP_NAV[2], // discover
      APP_NAV[1], // queue
      APP_NAV[6], // search
    ],
  },
  {
    id: "materials",
    label: "Materials",
    items: [
      APP_NAV[3], // documents
      APP_NAV[4], // library
      APP_NAV[5], // vault
    ],
  },
  {
    id: "insights",
    label: "Insights",
    items: [APP_NAV[7]], // analytics
  },
];

function NavLinkRow({
  href,
  label,
  description,
  icon: Icon,
  collapsed,
  active,
  count,
  onNavigate,
}: NavItem & {
  collapsed: boolean;
  active: boolean;
  count?: number;
  onNavigate?: () => void;
}) {
  return (
    <Link
      href={href}
      title={description}
      onClick={onNavigate}
      className={cn(
        "relative flex items-center gap-3 rounded-lg px-2.5 py-2 text-[0.9375rem] outline-none transition-colors",
        "focus-visible:ring-2 focus-visible:ring-ring",
        active
          ? "workspace-nav-active pl-3"
          : "text-sidebar-foreground/75 hover:bg-sidebar-accent/50 hover:text-sidebar-accent-foreground",
      )}
      aria-current={active ? "page" : undefined}
    >
      <Icon className="size-4 shrink-0" aria-hidden />
      {!collapsed ? (
        <>
          <span className="flex-1">{label}</span>
          {count !== undefined ? (
            <Badge variant="secondary" className="ml-auto tabular-nums text-xs">
              {count}
            </Badge>
          ) : null}
        </>
      ) : null}
      {collapsed ? <span className="sr-only">{label}</span> : null}
    </Link>
  );
}

export function NavLinks({
  collapsed = false,
  onNavigate,
  counts = {},
}: {
  collapsed?: boolean;
  onNavigate?: () => void;
  counts?: Record<string, number | undefined>;
}) {
  const pathname = usePathname();
  const { user } = useAuth();
  const admin = isAdmin(user);

  return (
    <div className="space-y-4">
      {NAV_SECTIONS.map((section) => (
        <div key={section.id}>
          {!collapsed ? (
            <p className="mb-1 px-2.5 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground/70">
              {section.label}
            </p>
          ) : null}
          <div className="space-y-0.5">
            {section.items.map((item) => {
              const active = pathname === item.href || pathname.startsWith(`${item.href}/`);
              return (
                <NavLinkRow
                  key={item.href}
                  {...item}
                  collapsed={collapsed}
                  active={active}
                  count={counts[item.href]}
                  onNavigate={onNavigate}
                />
              );
            })}
          </div>
        </div>
      ))}

      <div>
        {!collapsed ? (
          <p className="mb-1 px-2.5 font-mono text-[0.6rem] font-semibold uppercase tracking-[0.16em] text-muted-foreground/70">
            System
          </p>
        ) : null}
        <div className="space-y-0.5">
          {admin ? (
            <NavLinkRow
              href="/admin"
              label="Admin"
              description="Ops, users, cost, system"
              icon={Shield}
              collapsed={collapsed}
              active={pathname === "/admin" || pathname.startsWith("/admin/")}
              count={counts["/admin"]}
              onNavigate={onNavigate}
            />
          ) : null}
          <NavLinkRow
            href="/settings"
            label="Settings"
            icon={Settings}
            collapsed={collapsed}
            active={pathname === "/settings" || pathname.startsWith("/settings/")}
            count={counts["/settings"]}
            onNavigate={onNavigate}
          />
        </div>
      </div>
    </div>
  );
}
