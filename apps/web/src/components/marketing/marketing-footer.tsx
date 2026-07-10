import Link from "next/link";

const footerGroups = [
  {
    title: "Product",
    links: [
      { href: "/features", label: "Features" },
      { href: "/how-it-works", label: "How it works" },
      { href: "/pricing", label: "Pricing" },
      { href: "/faq", label: "FAQ" },
      { href: "/blog", label: "Blog" },
    ],
  },
  {
    title: "Company",
    links: [
      { href: "mailto:hello@jober.app", label: "Contact" },
      { href: "/login", label: "Sign in" },
      { href: "/signup", label: "Get started" },
    ],
  },
  {
    title: "Legal",
    links: [
      { href: "/privacy", label: "Privacy policy" },
      { href: "/terms", label: "Terms of service" },
      { href: "/acceptable-use", label: "Acceptable use" },
    ],
  },
] as const;

export function MarketingFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border/40 bg-muted/20" aria-label="Site footer">
      <div className="mx-auto grid max-w-6xl gap-10 px-6 py-14 md:grid-cols-[1.4fr_repeat(3,minmax(0,1fr))]">
        {/* Brand column */}
        <div className="space-y-4">
          <p className="text-base font-semibold text-foreground">Jober</p>
          <p className="max-w-xs text-sm leading-relaxed text-muted-foreground">
            Assisted job applications with human review before every submit. You stay in control.
          </p>
          <p className="font-mono text-xs text-primary/70">
            Review before every submit.
          </p>
        </div>

        {/* Link columns */}
        {footerGroups.map((group) => (
          <div key={group.title}>
            <h2 className="font-mono text-[10px] font-medium uppercase tracking-[0.22em] text-muted-foreground/60">
              {group.title}
            </h2>
            <ul className="mt-4 space-y-2.5">
              {group.links.map(({ href, label }) => (
                <li key={href}>
                  <Link
                    href={href}
                    className="text-sm text-muted-foreground transition-colors duration-150 hover:text-foreground"
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>

      {/* Bottom bar */}
      <div className="border-t border-border/40 px-6 py-4 text-center font-mono text-xs text-muted-foreground/60">
        © {year} Jober. All rights reserved.
      </div>
    </footer>
  );
}
