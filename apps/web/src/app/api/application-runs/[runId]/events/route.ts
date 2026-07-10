import { cookies } from "next/headers";

export const dynamic = "force-dynamic";

export async function GET(
  request: Request,
  context: { params: Promise<{ runId: string }> },
): Promise<Response> {
  const { runId } = await context.params;
  const apiBase = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
  const incoming = new URL(request.url);
  const target = `${apiBase}/api/application-runs/${runId}/events${incoming.search}`;

  const cookieStore = await cookies();
  const parts: string[] = [];
  const session = cookieStore.get("jober_session");
  const csrf = cookieStore.get("jober_csrf");
  if (session) parts.push(`jober_session=${session.value}`);
  if (csrf) parts.push(`jober_csrf=${csrf.value}`);

  // Mirror REST client: forward cookie session and optional dev-bypass identity.
  const headers: Record<string, string> = {};
  if (parts.length) headers.Cookie = parts.join("; ");
  const devBypass =
    process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS === "true" ||
    process.env.NEXT_PUBLIC_AUTH_MODE === "dev";
  if (devBypass) {
    const tenant =
      process.env.NEXT_PUBLIC_DEV_TENANT_ID ?? "00000000-0000-4000-8000-000000000001";
    const user =
      process.env.NEXT_PUBLIC_DEV_USER_ID ?? "00000000-0000-4000-8000-000000000002";
    headers["X-Jober-Tenant-Id"] = tenant;
    headers["X-Jober-User-Id"] = user;
  }

  const backend = await fetch(target, {
    headers,
    cache: "no-store",
  });

  return new Response(backend.body, {
    status: backend.status,
    headers: {
      "Content-Type": backend.headers.get("Content-Type") ?? "text/event-stream",
      "Cache-Control": "no-cache",
      Connection: "keep-alive",
    },
  });
}
