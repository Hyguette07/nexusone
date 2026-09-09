const API = process.env.NEXT_PUBLIC_API_URL ?? "http://localhost:8085/api/v1";
export const TOKEN_KEY = "nexusone.token";
export const USER_KEY = "nexusone.user";

export function getToken(): string | null {
  if (typeof window === "undefined") return null;
  return localStorage.getItem(TOKEN_KEY);
}

export function setToken(token: string | null) {
  if (typeof window === "undefined") return;
  if (token) localStorage.setItem(TOKEN_KEY, token);
  else localStorage.removeItem(TOKEN_KEY);
}

type Envelope<T> = {
  success?: boolean;
  message?: string;
  error?: string;
  detail?: string | unknown;
  data?: T;
};

export class ApiError extends Error {
  status: number;
  constructor(status: number, message: string) {
    super(message);
    this.status = status;
  }
}

function extractMessage(status: number, json: Envelope<unknown> | null, fallback: string) {
  if (!json) return fallback;
  if (typeof json.detail === "string") return json.detail;
  if (Array.isArray(json.detail)) {
    const first = json.detail[0] as { msg?: string };
    if (first?.msg) return first.msg;
  }
  return json.message || json.error || fallback || `Request failed (${status})`;
}

export async function api<T>(path: string, init: RequestInit = {}): Promise<T> {
  const token = getToken();
  const headers = new Headers(init.headers);
  if (init.body) headers.set("Content-Type", "application/json");
  if (token) headers.set("Authorization", `Bearer ${token}`);

  const res = await fetch(`${API}${path}`, { ...init, headers });
  if (res.status === 204) return undefined as T;

  const json = (await res.json().catch(() => null)) as Envelope<T> | null;
  if (!res.ok || json?.success === false) {
    throw new ApiError(res.status, extractMessage(res.status, json, "Request failed"));
  }
  if (json && "data" in json) return json.data as T;
  return json as T;
}
