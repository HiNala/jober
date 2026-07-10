"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { useState } from "react";
import {
  BarChart3,
  BookOpen,
  LockKeyhole,
  MoreHorizontal,
  Search,
  Settings,
  Shield,
} from "lucide-react";

import { useAuth } from "@/contexts/auth-context";
import { isAdmin } from "@/lib/auth/permissions";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { motionMicro } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const MORE_LINKS = [
  { href: "/library", label: "Library", icon: BookOpen, description: "Lists, letters, runs" },
  { href: "/vault", label: "Vault", icon: LockKeyhole, description: "Profile & resume" },
  { href: "/search", label: "Search", icon: Search, description: "Find in your workspace" },
  { href: "/analytics", label: "Analytics", icon: BarChart3, description: "Your apply funnel" },
  { href: "/settings", label: "Settings", icon: Settings, description: "Plan, AI, security" },
] as const;

/**
 * Overflow destinations for the mobile bottom tab “More” control.
 * Primary tabs stay Home / Discover / Queue / Docs.
 */
export function MobileMoreSheet({ active }: { active: boolean }) {
  const pathname = usePathname();
  const { user } = useAuth();
  const [open, setOpen] = useState(false);

  return (
    <Sheet open={open} onOpenChange={setOpen}>
      <SheetTrigger
        className="flex w-full flex-col items-center"
        render={
          <button
            type="button"
            className={cn(
              motionMicro,
              "flex min-h-11 w-full flex-col items-center justify-center gap-0.5 rounded-md px-1 py-1.5 text-[0.65rem] font-medium",
              active ? "text-primary" : "text-muted-foreground hover:text-foreground",
            )}
            aria-label="More destinations"
          >
            <MoreHorizontal className="size-5 shrink-0" aria-hidden />
            <span>More</span>
          </button>
        }
      />
      <SheetContent
        side="bottom"
        className="rounded-t-2xl border-border/80 bg-background pb-[max(1rem,env(safe-area-inset-bottom))]"
      >
        <SheetHeader className="text-left">
          <SheetTitle className="text-base font-semibold">More</SheetTitle>
        </SheetHeader>
        <nav className="mt-3 grid gap-1" aria-label="More destinations">
          {MORE_LINKS.map(({ href, label, icon: Icon, description }) => {
            const isCurrent = pathname === href || pathname.startsWith(`${href}/`);
            return (
              <Link
                key={href}
                href={href}
                onClick={() => setOpen(false)}
                className={cn(
                  "flex items-center gap-3 rounded-xl px-3 py-3 transition-colors",
                  isCurrent
                    ? "bg-primary/10 text-primary"
                    : "text-foreground hover:bg-muted/60",
                )}
                aria-current={isCurrent ? "page" : undefined}
              >
                <Icon className="size-5 shrink-0 opacity-80" aria-hidden />
                <span className="min-w-0 flex-1">
                  <span className="block text-sm font-medium">{label}</span>
                  <span className="block text-xs text-muted-foreground">{description}</span>
                </span>
              </Link>
            );
          })}
          {isAdmin(user) ? (
            <Link
              href="/admin"
              onClick={() => setOpen(false)}
              className={cn(
                "flex items-center gap-3 rounded-xl px-3 py-3 transition-colors",
                pathname.startsWith("/admin")
                  ? "bg-primary/10 text-primary"
                  : "text-foreground hover:bg-muted/60",
              )}
              aria-current={pathname.startsWith("/admin") ? "page" : undefined}
            >
              <Shield className="size-5 shrink-0 opacity-80" aria-hidden />
              <span className="min-w-0 flex-1">
                <span className="block text-sm font-medium">Admin</span>
                <span className="block text-xs text-muted-foreground">
                  Ops, users, cost, system
                </span>
              </span>
            </Link>
          ) : null}
        </nav>
        <div className="mt-3 flex justify-end px-1">
          <Button type="button" variant="ghost" size="sm" onClick={() => setOpen(false)}>
            Close
          </Button>
        </div>
      </SheetContent>
    </Sheet>
  );
}
