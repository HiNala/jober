"use client";

import Link from "next/link";
import { Menu } from "lucide-react";

import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { motionPress } from "@/lib/design/motion";
import { cn } from "@/lib/utils";

const LINKS = [
  { href: "/features", label: "Features" },
  { href: "/how-it-works", label: "How it works" },
  { href: "/pricing", label: "Pricing" },
  { href: "/faq", label: "FAQ" },
  { href: "/blog", label: "Blog" },
] as const;

export function MarketingMobileNav() {
  return (
    <Sheet>
      <SheetTrigger
        className="lg:hidden"
        render={
          <Button
            variant="ghost"
            className={cn("size-11 shrink-0", motionPress)}
            aria-label="Open marketing menu"
          >
            <Menu className="size-5" aria-hidden />
          </Button>
        }
      />
      <SheetContent side="left" className="w-72">
        <SheetHeader>
          <SheetTitle>Menu</SheetTitle>
        </SheetHeader>
        <nav className="mt-4 flex flex-col gap-1" aria-label="Marketing">
          {LINKS.map(({ href, label }) => (
            <Link
              key={href}
              href={href}
              className="rounded-md px-3 py-3 text-base font-medium text-foreground hover:bg-muted"
            >
              {label}
            </Link>
          ))}
        </nav>
      </SheetContent>
    </Sheet>
  );
}
