"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";

import { useAuth } from "@/contexts/auth-context";
import { isAdmin } from "@/lib/auth/permissions";
import {
  BarChart3,
  BookOpen,
  Compass,
  LayoutDashboard,
  ListTodo,
  Search,
  Settings,
  Shield,
  type LucideIcon,
} from "lucide-react";

import { cn } from "@/lib/utils";

export const APP_NAV: {
  href: string;
  label: string;
  icon: LucideIcon;
}[] = [
  { href: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { href: "/queue", label: "Queue", icon: ListTodo },
  { href: "/discover", label: "Discover", icon: Compass },
  { href: "/library", label: "Library", icon: BookOpen },
  { href: "/search", label: "Search", icon: Search },
  { href: "/analytics", label: "Analytics", icon: BarChart3 },
  { href: "/settings", label: "Settings", icon: Settings },
];

export function NavLinks({
  collapsed = false,
  onNavigate,
}: {
  collapsed?: boolean;
  onNavigate?: () => void;
}) {
  const pathname = usePathname();
  const { user } = useAuth();
  const nav = isAdmin(user)
    ? [
        ...APP_NAV.slice(0, 6),
        { href: "/admin", label: "Admin", icon: Shield },
        ...APP_NAV.slice(6),
      ]
    : APP_NAV;

  return (
    <>
      {nav.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-md px-2.5 py-2 text-base font-medium outline-none transition-colors",
              "focus-visible:ring-2 focus-visible:ring-ring",
              active
                ? "bg-sidebar-accent text-sidebar-accent-foreground"
                : "text-sidebar-foreground/80 hover:bg-sidebar-accent/60 hover:text-sidebar-accent-foreground",
            )}
            aria-current={active ? "page" : undefined}
          >
            <Icon className="size-4 shrink-0" aria-hidden />
            {!collapsed ? <span>{label}</span> : null}
            {collapsed ? <span className="sr-only">{label}</span> : null}
          </Link>
        );
      })}
    </>
  );
}
