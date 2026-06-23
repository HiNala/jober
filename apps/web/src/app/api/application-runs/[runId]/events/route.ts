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

  const backend = await fetch(target, {
    headers: parts.length ? { Cookie: parts.join("; ") } : {},
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
