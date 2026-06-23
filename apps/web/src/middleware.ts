import { NextResponse } from "next/server";
import type { NextRequest } from "next/server";

const BYPASS =
  process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS === "true" ||
  process.env.NEXT_PUBLIC_AUTH_MODE === "dev";

const PROTECTED_PREFIXES = [
  "/dashboard",
  "/queue",
  "/documents",
  "/vault",
  "/settings",
  "/runs",
  "/discover",
  "/library",
  "/search",
  "/analytics",
  "/admin",
];

export function middleware(request: NextRequest) {
  if (BYPASS) {
    return NextResponse.next();
  }

  const { pathname } = request.nextUrl;
  const isProtected = PROTECTED_PREFIXES.some(
    (prefix) => pathname === prefix || pathname.startsWith(`${prefix}/`),
  );
  if (!isProtected) {
    return NextResponse.next();
  }

  const session = request.cookies.get("jober_session");
  if (!session?.value) {
    const login = new URL("/login", request.url);
    login.searchParams.set("next", pathname);
    return NextResponse.redirect(login);
  }

  return NextResponse.next();
}

export const config = {
  matcher: [
    "/dashboard/:path*",
    "/queue/:path*",
    "/documents/:path*",
    "/vault/:path*",
    "/settings/:path*",
    "/runs/:path*",
    "/discover/:path*",
    "/library/:path*",
    "/search/:path*",
    "/analytics/:path*",
    "/admin/:path*",
  ],
};
