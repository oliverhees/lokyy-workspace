"use client";

import { useLocale } from "next-intl";

// Switches UI language by setting the `locale` cookie and reloading.
// DE default, EN switchable — i18n is base architecture (CLAUDE.md).
export function LanguageSwitch() {
  const locale = useLocale();

  function choose(l: string) {
    if (l === locale) return;
    document.cookie = `locale=${l};path=/;max-age=31536000;samesite=lax`;
    window.location.reload();
  }

  return (
    <div className="flex overflow-hidden rounded-lg border border-slate-300 text-xs dark:border-slate-700">
      {(["de", "en"] as const).map((l) => (
        <button
          key={l}
          onClick={() => choose(l)}
          className={locale === l ? "grad px-2 py-1.5 font-semibold text-white" : "px-2 py-1.5 text-slate-500"}
        >
          {l.toUpperCase()}
        </button>
      ))}
    </div>
  );
}
