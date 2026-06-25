"use client";

// M2.1 — edit the agent's persona (soul) and the user profile that flow into the
// chat system prompt. Markdown text; takes effect on the next message.
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { type AgentContext, fetchContext, updateContext } from "@/lib/context";

const areaClass =
  "w-full resize-y rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/30 dark:border-slate-700 dark:bg-slate-900";

export function AgentTab() {
  const t = useTranslations("agent");
  const [data, setData] = useState<AgentContext | null>(null);
  const [soul, setSoul] = useState("");
  const [profile, setProfile] = useState("");
  const [busy, setBusy] = useState(false);
  const [hint, setHint] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchContext()
      .then((c) => {
        setData(c);
        setSoul(c.soul);
        setProfile(c.user_profile);
      })
      .catch(() => setError(t("loadError")));
  }, [t]);

  async function save() {
    setBusy(true);
    setError(null);
    try {
      const c = await updateContext({ soul, user_profile: profile });
      setData(c);
      setHint(t("saved"));
      setTimeout(() => setHint(null), 1800);
    } catch {
      setError(t("saveError"));
    } finally {
      setBusy(false);
    }
  }

  if (!data) {
    return <div className="p-2 text-sm text-slate-400">{error ?? "…"}</div>;
  }

  const dirty = soul !== data.soul || profile !== data.user_profile;

  return (
    <div className="space-y-5">
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-200">
          {t("soul")}
        </label>
        <p className="mb-1.5 text-xs text-slate-400">{t("soulHint")}</p>
        <textarea className={areaClass} rows={6} value={soul} onChange={(e) => setSoul(e.target.value)} />
      </div>
      <div>
        <label className="mb-1 block text-sm font-medium text-slate-700 dark:text-slate-200">
          {t("profile")}
        </label>
        <p className="mb-1.5 text-xs text-slate-400">{t("profileHint")}</p>
        <textarea className={areaClass} rows={6} value={profile} onChange={(e) => setProfile(e.target.value)}
                  placeholder={t("profilePlaceholder")} />
      </div>
      {error && <p className="text-sm text-red-500">{error}</p>}
      <div className="flex items-center gap-3">
        <button
          type="button"
          onClick={save}
          disabled={busy || !dirty}
          className="grad rounded-lg px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-40"
        >
          {t("save")}
        </button>
        {hint && <span className="text-xs font-medium text-emerald-500">{hint}</span>}
      </div>
    </div>
  );
}
