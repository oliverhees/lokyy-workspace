// Minimal API client against the active backend (see connection.ts).
import { getApiBase } from "./connection";

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  return fetch(getApiBase() + path, { credentials: "include", ...init });
}

export async function checkHealth(base?: string): Promise<boolean> {
  try {
    const res = await fetch((base ?? getApiBase()) + "/health", { cache: "no-store" });
    if (!res.ok) return false;
    const data = (await res.json()) as { status?: string };
    return data.status === "ok";
  } catch {
    return false;
  }
}
