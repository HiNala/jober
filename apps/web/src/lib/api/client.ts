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

function authHeaders(): Record<string, string> {
  const headers: Record<string, string> = {};
  const tenantId = process.env.NEXT_PUBLIC_JOBER_TENANT_ID;
  const userId = process.env.NEXT_PUBLIC_JOBER_USER_ID;
  if (tenantId) headers["X-Jober-Tenant-Id"] = tenantId;
  if (userId) headers["X-Jober-User-Id"] = userId;
  return headers;
}

export async function apiFetch<T>(
  path: string,
  init?: RequestInit,
): Promise<T> {
  const url = `${getApiBaseUrl()}${path}`;
  const res = await fetch(url, {
    ...init,
    headers: {
      Accept: "application/json",
      ...authHeaders(),
      ...init?.headers,
    },
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.text().catch(() => undefined);
    throw new ApiError(`API ${res.status}: ${path}`, res.status, body);
  }

  if (res.status === 204) {
    return undefined as T;
  }

  return res.json() as Promise<T>;
}
