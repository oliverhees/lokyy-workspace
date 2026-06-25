// Settings API client (F3) — the central preference store. Server-side source of
// truth so settings survive device switches; the client mirrors theme/connection
// into localStorage for instant application.
import { apiFetch } from "./api";

export type Language = "de" | "en";
export type Theme = "dark" | "light" | "system";
export type ConnectionDefault = "local" | "remote";

export interface Settings {
  language: Language;
  theme: Theme;
  connection_default: ConnectionDefault;
  display_name: string;
  email: string;
  is_org_admin: boolean;
}

export async function fetchSettings(): Promise<Settings> {
  const res = await apiFetch("/settings");
  if (!res.ok) throw new Error(`settings load failed: ${res.status}`);
  return (await res.json()) as Settings;
}

export interface SettingsPatch {
  language?: Language;
  theme?: Theme;
  connection_default?: ConnectionDefault;
}

export async function updateSettings(patch: SettingsPatch): Promise<Settings> {
  const res = await apiFetch("/settings", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`settings update failed: ${res.status}`);
  return (await res.json()) as Settings;
}

export async function updateProfile(displayName: string): Promise<Settings> {
  const res = await apiFetch("/settings/profile", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ display_name: displayName }),
  });
  if (!res.ok) throw new Error(`profile update failed: ${res.status}`);
  return (await res.json()) as Settings;
}
