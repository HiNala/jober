import { getApiBaseUrl } from "@/lib/api/client";

export type AuthUser = {
  id: string;
  email: string;
  display_name: string | null;
  tenant_id: string;
  email_verified: boolean;
  status: string;
  role: string;
  plan: string;
  last_login_at: string | null;
};

function csrfToken(): string | undefined {
  if (typeof document === "undefined") return undefined;
  const match = document.cookie.match(/(?:^|;\s*)jober_csrf=([^;]+)/);
  return match?.[1] ? decodeURIComponent(match[1]) : undefined;
}

export async function authFetch<T>(path: string, init?: RequestInit): Promise<T> {
  const method = init?.method?.toUpperCase() ?? "GET";
  const headers: Record<string, string> = {
    Accept: "application/json",
    ...(init?.headers as Record<string, string> | undefined),
  };
  if (method !== "GET" && method !== "HEAD") {
    const token = csrfToken();
    if (token) headers["X-CSRF-Token"] = token;
  }
  if (init?.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }

  const res = await fetch(`${getApiBaseUrl()}${path}`, {
    ...init,
    credentials: "include",
    headers,
    cache: "no-store",
  });

  if (!res.ok) {
    const body = await res.text().catch(() => undefined);
    throw new Error(body || `Auth ${res.status}`);
  }
  if (res.status === 204) return undefined as T;
  return res.json() as Promise<T>;
}

export function fetchMe() {
  return authFetch<AuthUser>("/api/auth/me");
}

export function login(email: string, password: string) {
  return authFetch<AuthUser>("/api/auth/login", {
    method: "POST",
    body: JSON.stringify({ email, password }),
  });
}

export function register(email: string, password: string, displayName?: string) {
  return authFetch<AuthUser>("/api/auth/register", {
    method: "POST",
    body: JSON.stringify({ email, password, display_name: displayName }),
  });
}

export function logout() {
  return authFetch<{ message: string }>("/api/auth/logout", { method: "POST" });
}

export function forgotPassword(email: string) {
  return authFetch<{ message: string }>("/api/auth/forgot-password", {
    method: "POST",
    body: JSON.stringify({ email }),
  });
}

export function resetPassword(token: string, newPassword: string) {
  return authFetch<{ message: string }>("/api/auth/reset-password", {
    method: "POST",
    body: JSON.stringify({ token, new_password: newPassword }),
  });
}

export function refreshSession() {
  return authFetch<{ message: string }>("/api/auth/refresh", { method: "POST" });
}

export type SessionList = {
  active_sessions: number;
  session_ids: string[];
};

export function fetchSessions() {
  return authFetch<SessionList>("/api/auth/sessions");
}

export function logoutAll() {
  return authFetch<{ message: string }>("/api/auth/logout-all", { method: "POST" });
}
