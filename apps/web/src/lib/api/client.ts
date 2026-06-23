export class ApiError extends Error {
  constructor(
    message: string,
    public readonly status: number,
    public readonly body?: string,
  ) {
    super(message);
    this.name = "ApiError";
  }
}

export function getApiBaseUrl(): string {
  return process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8000";
}

const DEV_BYPASS =
  process.env.NEXT_PUBLIC_DEV_AUTH_BYPASS === "true" ||
  process.env.NEXT_PUBLIC_AUTH_MODE === "dev";

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  if (DEV_BYPASS) {
    const tenantId = process.env.NEXT_PUBLIC_JOBER_TENANT_ID;
    const userId = process.env.NEXT_PUBLIC_JOBER_USER_ID;
    if (tenantId) headers["X-Jober-Tenant-Id"] = tenantId;
    if (userId) headers["X-Jober-User-Id"] = userId;
  }
  return headers;
}

function csrfHeader(init?: RequestInit): Record<string, string> {
  if (typeof document === "undefined") return {};
  const method = init?.method?.toUpperCase() ?? "GET";
  if (method === "GET" || method === "HEAD") return {};
  const match = document.cookie.match(/(?:^|;\s*)jober_csrf=([^;]+)/);
  const token = match?.[1] ? decodeURIComponent(match[1]) : undefined;
  return token ? { "X-CSRF-Token": token } : {};
}

function jsonContentType(init?: RequestInit): Record<string, string> {
  if (init?.body == null || init.body instanceof FormData) {
    return {};
  }
  const hasContentType = init.headers
    ? new Headers(init.headers).has("Content-Type")
    : false;
  return hasContentType ? {} : { "Content-Type": "application/json" };
}

export async function uploadFetch(path: string, form: FormData): Promise<Response> {
  const url = `${getApiBaseUrl()}${path}`;
  return fetch(url, {
    method: "POST",
    credentials: "include",
    headers: {
      ...authHeaders(),
      ...csrfHeader({ method: "POST" }),
    },
    body: form,
    cache: "no-store",
  });
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`;
  const res = await fetch(url, {
    ...init,
    credentials: "include",
    headers: {
      Accept: "application/json",
      ...authHeaders(),
      ...jsonContentType(init),
      ...csrfHeader(init),
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (res.status === 401 && !DEV_BYPASS && !path.startsWith("/api/auth/")) {
    const { tryRecoverSession, markSessionExpired } = await import("./session-recovery");
    const recovered = await tryRecoverSession();
    if (recovered) {
      return apiFetch<T>(path, init);
    }
    markSessionExpired();
  }

  if (!res.ok) {
    const body = await res.text().catch(() => undefined);
    throw new ApiError(`API ${res.status}: ${path}`, res.status, body);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}
