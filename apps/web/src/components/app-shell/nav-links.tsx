"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import {
  FileText,
  LayoutDashboard,
  ListTodo,
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
  { href: "/documents", label: "Documents", icon: FileText },
  { href: "/vault", label: "Vault", icon: Shield },
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

  return (
    <>
      {APP_NAV.map(({ href, label, icon: Icon }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            onClick={onNavigate}
            className={cn(
              "flex items-center gap-3 rounded-md px-2.5 py-2 text-sm outline-none transition-colors",
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
