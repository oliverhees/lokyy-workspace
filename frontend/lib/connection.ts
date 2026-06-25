// Connection layer: the frontend is a thin PWA that talks to a configurable
// backend — local machine OR own server. The user switches at runtime.
// (Core of M0/T0.5; see docs/KONZEPT.md K5.)
export type ConnMode = "local" | "remote";

const LOCAL_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "http://localhost:8008";
const REMOTE_URL = process.env.NEXT_PUBLIC_SERVER_URL || "";
const STORAGE_KEY = "lokyy.connMode";

export function hasRemote(): boolean {
  return REMOTE_URL.length > 0;
}

export function getMode(): ConnMode {
  if (typeof window === "undefined") return "local";
  const m = window.localStorage.getItem(STORAGE_KEY);
  return m === "remote" && hasRemote() ? "remote" : "local";
}

export function setMode(mode: ConnMode): void {
  if (typeof window !== "undefined") {
    window.localStorage.setItem(STORAGE_KEY, mode);
  }
}

export function apiBaseFor(mode: ConnMode): string {
  return mode === "remote" && hasRemote() ? REMOTE_URL : LOCAL_URL;
}

export function getApiBase(): string {
  return apiBaseFor(getMode());
}
