// Auth API client (F1) — talks to the backend /auth/* routes via the active
// connection (local/server). Sessions ride on an httpOnly cookie, so every call
// uses credentials: "include" (apiFetch already does). No tokens in JS land.
import { apiFetch } from "./api";

export interface AuthUser {
  id: string;
  email: string;
  display_name: string;
  is_org_admin: boolean;
  totp_enabled: boolean;
}

/** Raised on any auth failure; `status` lets callers tailor the message. */
export class AuthApiError extends Error {
  constructor(public status: number, message: string) {
    super(message);
    this.name = "AuthApiError";
  }
}

async function parseError(res: Response): Promise<never> {
  let detail = `request failed (${res.status})`;
  try {
    const data = (await res.json()) as { detail?: string };
    if (data?.detail) detail = data.detail;
  } catch {
    // non-JSON body — keep the generic message
  }
  throw new AuthApiError(res.status, detail);
}

export interface SignupInput {
  organization_name: string;
  email: string;
  password: string;
  display_name: string;
}

/** Bootstrap a fresh instance: creates org + first admin and logs in. */
export async function signup(input: SignupInput): Promise<AuthUser> {
  const res = await apiFetch("/auth/signup", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) return parseError(res);
  return (await res.json()) as AuthUser;
}

export interface LoginInput {
  email: string;
  password: string;
  totp_code?: string;
}

export async function login(input: LoginInput): Promise<AuthUser> {
  const res = await apiFetch("/auth/login", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) return parseError(res);
  return (await res.json()) as AuthUser;
}

/** Resolve the current session. Returns null when not authenticated (401). */
export async function fetchMe(): Promise<AuthUser | null> {
  const res = await apiFetch("/auth/me");
  if (res.status === 401) return null;
  if (!res.ok) return parseError(res);
  return (await res.json()) as AuthUser;
}

export async function logout(): Promise<void> {
  await apiFetch("/auth/logout", { method: "POST" });
}
