"use client";

import { Menu } from "lucide-react";

import { NavLinks } from "@/components/app-shell/nav-links";
import { Button } from "@/components/ui/button";
import {
  Sheet,
  SheetContent,
  SheetHeader,
  SheetTitle,
  SheetTrigger,
} from "@/components/ui/sheet";
import { useUiStore } from "@/stores/ui-store";

export function MobileNav() {
  const { mobileNavOpen, setMobileNavOpen } = useUiStore();

  return (
    <Sheet open={mobileNavOpen} onOpenChange={setMobileNavOpen}>
      <SheetTrigger
        className="md:hidden"
        render={
          <Button variant="ghost" size="icon-sm" aria-label="Open navigation menu">
            <Menu className="size-4" />
          </Button>
        }
      />
      <SheetContent side="left" className="w-64 bg-sidebar p-0 text-sidebar-foreground">
        <SheetHeader className="border-b border-sidebar-border px-4 py-3 text-left">
          <SheetTitle className="text-sm font-semibold">Jober</SheetTitle>
        </SheetHeader>
        <nav className="flex flex-col gap-1 p-2" aria-label="Main navigation">
          <NavLinks onNavigate={() => setMobileNavOpen(false)} />
        </nav>
      </SheetContent>
    </Sheet>
  );
}
