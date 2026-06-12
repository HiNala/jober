export type BlogPost = {
  slug: string;
  title: string;
  summary: string;
  publishedAt: string;
  body: string[];
};

/** Static blog posts shipped with the web app. */
export const BLOG_POSTS: BlogPost[] = [
  {
    slug: "welcome-to-jober",
    title: "Welcome to Jober",
    summary: "Assisted applications with review before submit — and why we built it that way.",
    publishedAt: "2026-06-09",
    body: [
      "Jober helps you apply to jobs you choose — with tailored materials, visible run consoles, and explicit approval before anything submits.",
      "We are not an auto-apply bot. CAPTCHAs, logins, and sensitive fields pause for you. That posture is a product decision, not a footnote.",
      "This changelog will carry launch updates, policy changes, and product notes. Subscribe by bookmarking /blog or following the repo.",
    ],
  },
];

export function postBySlug(slug: string): BlogPost | undefined {
  return BLOG_POSTS.find((p) => p.slug === slug);
}

export function blogSlugs(): string[] {
  return BLOG_POSTS.map((p) => p.slug);
}
