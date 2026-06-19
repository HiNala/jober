"use client";

import Link from "next/link";
import { usePathname } from "next/navigation";
import { cn } from "@/lib/utils";

const navLinks = [
  { href: "/features", label: "Features" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/faq", label: "FAQ" },
] as const;

export function MarketingNav() {
  const pathname = usePathname();

  return (
    <nav aria-label="Marketing" className="hidden flex-1 items-center justify-center gap-1 lg:flex">
      {navLinks.map(({ href, label }) => {
        const active = pathname === href || pathname.startsWith(`${href}/`);
        return (
          <Link
            key={href}
            href={href}
            className={cn(
              "rounded-full px-3.5 py-1.5 text-[15px] font-medium motion-safe:transition-colors motion-safe:duration-200",
              active
                ? "bg-muted/80 text-foreground"
                : "text-muted-foreground hover:bg-muted/50 hover:text-foreground",
            )}
            aria-current={active ? "page" : undefined}
          >
            {label}
          </Link>
        );
      })}
    </nav>
  );
}
