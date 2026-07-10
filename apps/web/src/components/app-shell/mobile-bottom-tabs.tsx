"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { Compass, FileText, Home, ListTodo } from "lucide-react";

import { MobileMoreSheet } from "@/components/app-shell/mobile-more-sheet";
import { cn } from "@/lib/utils";
import { motionMicro } from "@/lib/design/motion";

const PRIMARY_TABS = [
  { href: "/dashboard", label: "Home", icon: Home },
  { href: "/discover", label: "Discover", icon: Compass },
  { href: "/queue", label: "Queue", icon: ListTodo },
  { href: "/documents", label: "Docs", icon: FileText },
] as const;

function isPrimaryActive(pathname: string, href: string): boolean {
  if (href === "/dashboard") {
    return pathname === "/dashboard" || pathname === "/";
  }
  return pathname === href || pathname.startsWith(`${href}/`);
}

function isMoreActive(pathname: string): boolean {
  return (
    pathname.startsWith("/settings") ||
    pathname.startsWith("/vault") ||
    pathname.startsWith("/library") ||
    pathname.startsWith("/analytics") ||
    pathname.startsWith("/admin") ||
    pathname.startsWith("/search")
  );
}

/** Fixed bottom tab bar for small viewports (Mission 44 + More sheet). */
export function MobileBottomTabs() {
  const pathname = usePathname();

  return (
    <nav
      aria-label="Primary"
      className={cn(
        "fixed inset-x-0 bottom-0 z-40 border-t border-border/80 bg-background/95 backdrop-blur-md lg:hidden",
        "pb-[max(0.5rem,env(safe-area-inset-bottom))]",
      )}
    >
      <ul className="mx-auto flex max-w-lg items-stretch justify-between px-1 pt-1">
        {PRIMARY_TABS.map(({ href, label, icon: Icon }) => {
          const active = isPrimaryActive(pathname, href);
          return (
            <li key={href} className="flex-1">
              <Link
                href={href}
                className={cn(
                  motionMicro,
                  "flex min-h-11 flex-col items-center justify-center gap-0.5 rounded-md px-1 py-1.5 text-[0.65rem] font-medium",
                  active
                    ? "text-primary"
                    : "text-muted-foreground hover:text-foreground",
                )}
                aria-current={active ? "page" : undefined}
              >
                <Icon className="size-5 shrink-0" aria-hidden />
                <span>{label}</span>
              </Link>
            </li>
          );
        })}
        <li className="flex-1">
          <MobileMoreSheet active={isMoreActive(pathname)} />
        </li>
      </ul>
    </nav>
  );
}
