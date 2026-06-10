/**
 * Capture full-page screenshots of marketing + in-app routes.
 *
 * Usage (production):
 *   PLAYWRIGHT_SKIP_WEB_SERVER=1 PLAYWRIGHT_BASE_URL=https://web-production-29902.up.railway.app \
 *     node scripts/capture-screenshots.mjs
 */
import { chromium } from "@playwright/test";
import { mkdir } from "node:fs/promises";
import path from "node:path";
import { fileURLToPath } from "node:url";

const __dirname = path.dirname(fileURLToPath(import.meta.url));

const BASE_URL =
  process.env.PLAYWRIGHT_BASE_URL ?? "https://web-production-29902.up.railway.app";
const API_URL =
  process.env.API_URL ??
  process.env.NEXT_PUBLIC_API_URL ??
  "https://api-production-4b5b.up.railway.app";
const OUT_DIR =
  process.env.SCREENSHOT_DIR ??
  path.resolve(__dirname, "../../../docs/screenshots/prod");

/** @type {{ slug: string; path: string }[]} */
const PUBLIC_ROUTES = [
  { slug: "01-home", path: "/" },
  { slug: "02-features", path: "/features" },
  { slug: "03-how-it-works", path: "/how-it-works" },
  { slug: "04-pricing", path: "/pricing" },
  { slug: "05-faq", path: "/faq" },
  { slug: "06-blog", path: "/blog" },
  { slug: "07-blog-welcome-to-jober", path: "/blog/welcome-to-jober" },
  { slug: "08-privacy", path: "/privacy" },
  { slug: "09-terms", path: "/terms" },
  { slug: "10-acceptable-use", path: "/acceptable-use" },
  { slug: "11-login", path: "/login" },
  { slug: "12-signup", path: "/signup" },
  { slug: "13-forgot-password", path: "/forgot-password" },
];

/** @type {{ slug: string; path: string }[]} */
const APP_ROUTES = [
  { slug: "14-dashboard", path: "/dashboard" },
  { slug: "15-queue", path: "/queue" },
  { slug: "16-discover", path: "/discover" },
  { slug: "17-library-resumes", path: "/library?tab=resumes" },
  { slug: "18-library-letters", path: "/library?tab=letters" },
  { slug: "19-library-jobs", path: "/library?tab=jobs" },
  { slug: "20-library-runs", path: "/library?tab=runs" },
  { slug: "21-search", path: "/search" },
  { slug: "22-analytics", path: "/analytics" },
  { slug: "23-settings", path: "/settings" },
];

async function dismissConsentBanner(page) {
  const accept = page.getByRole("button", { name: /accept analytics/i });
  if (await accept.isVisible().catch(() => false)) {
    await accept.click();
  }
}

async function capture(page, slug) {
  await page.waitForLoadState("domcontentloaded");
  await dismissConsentBanner(page);
  await page.waitForTimeout(1200);
  const file = path.join(OUT_DIR, `${slug}.png`);
  await page.screenshot({ path: file, fullPage: true });
  console.log(`saved ${slug}.png`);
}

async function authenticate(context, page) {
  const email = `screenshots+${Date.now()}@example.com`;
  const password = "ScreenshotTest123!";

  await page.goto(`${BASE_URL}/`, { waitUntil: "domcontentloaded" });
  const registered = await page.evaluate(
    async ({ apiUrl, email, password }) => {
      const res = await fetch(`${apiUrl}/api/auth/register`, {
        method: "POST",
        credentials: "include",
        headers: { Accept: "application/json", "Content-Type": "application/json" },
        body: JSON.stringify({ email, password, display_name: "Screenshot User" }),
      });
      if (!res.ok) return { ok: false, body: await res.text() };
      return { ok: true };
    },
    { apiUrl: API_URL, email, password },
  );
  if (!registered.ok) {
    throw new Error(`register failed: ${registered.body}`);
  }
  console.log(`signed up as ${email}`);

  // Next.js middleware checks jober_session on the web origin; API sets it on the API host.
  const apiCookies = await context.cookies(API_URL);
  const session = apiCookies.find((c) => c.name === "jober_session");
  if (!session?.value) {
    throw new Error("missing jober_session after register");
  }
  const webHost = new URL(BASE_URL).hostname;
  await context.addCookies([
    {
      name: "jober_session",
      value: session.value,
      domain: webHost,
      path: "/",
      secure: true,
      sameSite: "Lax",
    },
  ]);

  await page.goto(`${BASE_URL}/dashboard`, { waitUntil: "domcontentloaded", timeout: 60_000 });
  await page.waitForURL(/\/dashboard/, { timeout: 45_000 });
}

async function main() {
  await mkdir(OUT_DIR, { recursive: true });

  const browser = await chromium.launch({
    headless: true,
    args: [
      "--disable-features=ThirdPartyCookiePhaseout,TrackingProtection3pcd",
    ],
  });
  const context = await browser.newContext({
    viewport: { width: 1440, height: 900 },
    deviceScaleFactor: 1,
  });
  const page = await context.newPage();

  for (const { slug, path: route } of PUBLIC_ROUTES) {
    await page.goto(`${BASE_URL}${route}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
    await capture(page, slug);
  }

  await authenticate(context, page);

  for (const { slug, path: route } of APP_ROUTES) {
    await page.goto(`${BASE_URL}${route}`, { waitUntil: "domcontentloaded", timeout: 60_000 });
    await capture(page, slug);
  }

  await browser.close();
  console.log(`\nDone — ${PUBLIC_ROUTES.length + APP_ROUTES.length} screenshots in ${OUT_DIR}`);
}

main().catch((err) => {
  console.error(err);
  process.exit(1);
});
