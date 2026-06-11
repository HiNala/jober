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
      { href: "/privacy", label: "Privacy" },
      { href: "/terms", label: "Terms" },
      { href: "/acceptable-use", label: "Acceptable use" },
    ],
  },
] as const;

export function MarketingFooter() {
  const year = new Date().getFullYear();

  return (
    <footer className="border-t border-border/60 bg-muted/20">
      <div className="mx-auto grid max-w-6xl gap-10 px-6 py-12 md:grid-cols-[1.2fr_repeat(3,minmax(0,1fr))]">
        <div className="space-y-3">
          <p className="text-base font-semibold">Jober</p>
          <p className="max-w-xs text-sm text-muted-foreground">
            Assisted job applications with human review before every submit. You stay in control.
          </p>
        </div>
        {footerGroups.map((group) => (
          <div key={group.title}>
            <h2 className="font-mono text-xs font-medium uppercase tracking-[0.18em] text-muted-foreground">
              {group.title}
            </h2>
            <ul className="mt-3 space-y-2">
              {group.links.map(({ href, label }) => (
                <li key={href}>
                  <Link
                    href={href}
                    className="text-sm text-foreground/80 transition-colors hover:text-foreground"
                  >
                    {label}
                  </Link>
                </li>
              ))}
            </ul>
          </div>
        ))}
      </div>
      <div className="border-t border-border/40 px-6 py-4 text-center text-xs text-muted-foreground">
        © {year} Jober. All rights reserved.
      </div>
    </footer>
  );
}
