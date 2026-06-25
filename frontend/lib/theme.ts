// Theme application (F3). The server stores the preference; the client mirrors it
// into localStorage so it can be applied instantly (incl. before hydration, via the
// inline script in app/layout.tsx) without a flash of the wrong theme.
export type Theme = "dark" | "light" | "system";

export const THEME_KEY = "lokyy.theme";

export function resolveTheme(theme: Theme): "dark" | "light" {
  if (theme === "system") {
    return typeof window !== "undefined" &&
      window.matchMedia("(prefers-color-scheme: dark)").matches
      ? "dark"
      : "light";
  }
  return theme;
}

export function applyTheme(theme: Theme): void {
  if (typeof document === "undefined") return;
  document.documentElement.classList.toggle("dark", resolveTheme(theme) === "dark");
}

export function storeTheme(theme: Theme): void {
  if (typeof window !== "undefined") window.localStorage.setItem(THEME_KEY, theme);
}

export function getStoredTheme(): Theme {
  if (typeof window === "undefined") return "dark";
  const t = window.localStorage.getItem(THEME_KEY);
  return t === "light" || t === "system" ? t : "dark";
}
