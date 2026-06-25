"use client";

// F3 / F3.1 — Settings page with in-page tab navigation. Each tab is a section
// (profile, appearance, connection); F4 adds a "models" tab here. Preferences
// persist server-side (source of truth) and apply on the client immediately.
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth/AuthProvider";
import { setMode } from "@/lib/connection";
import {
  type ConnectionDefault,
  type Language,
  type Settings,
  type Theme,
  fetchSettings,
  updateProfile,
  updateSettings,
} from "@/lib/settings";
import { applyTheme, storeTheme } from "@/lib/theme";
import { ModelsTab } from "@/components/settings/ModelsTab";
import { AgentTab } from "@/components/settings/AgentTab";

const fieldClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/30 dark:border-slate-700 dark:bg-slate-900";

const TABS = ["profile", "agent", "appearance", "models", "connection"] as const;
type Tab = (typeof TABS)[number];

function Row({ label, children }: { label: string; children: React.ReactNode }) {
  return (
    <label className="flex flex-col gap-1.5 sm:flex-row sm:items-center sm:justify-between sm:gap-4">
      <span className="text-sm text-slate-600 dark:text-slate-300">{label}</span>
      <div className="sm:w-64">{children}</div>
    </label>
  );
}

export default function SettingsPage() {
  const t = useTranslations("settings");
  const { refresh } = useAuth();

  const [tab, setTab] = useState<Tab>("profile");
  const [data, setData] = useState<Settings | null>(null);
  const [name, setName] = useState("");
  const [savingName, setSavingName] = useState(false);
  const [savedHint, setSavedHint] = useState<string | null>(null);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchSettings()
      .then((s) => {
        setData(s);
        setName(s.display_name);
      })
      .catch(() => setError(t("loadError")));
  }, [t]);

  function flashSaved() {
    setSavedHint(t("saved"));
    setTimeout(() => setSavedHint(null), 1800);
  }

  async function saveName() {
    if (!data || !name.trim()) return;
    setSavingName(true);
    setError(null);
    try {
      const s = await updateProfile(name.trim());
      setData(s);
      await refresh(); // keep the user menu name in sync
      flashSaved();
    } catch {
      setError(t("saveError"));
    } finally {
      setSavingName(false);
    }
  }

  async function changeTheme(theme: Theme) {
    if (!data) return;
    setData({ ...data, theme });
    storeTheme(theme);
    applyTheme(theme); // instant
    try {
      await updateSettings({ theme });
      flashSaved();
    } catch {
      setError(t("saveError"));
    }
  }

  async function changeConnection(connection_default: ConnectionDefault) {
    if (!data) return;
    setData({ ...data, connection_default });
    setMode(connection_default); // mirror into the active connection switch
    try {
      await updateSettings({ connection_default });
      flashSaved();
    } catch {
      setError(t("saveError"));
    }
  }

  async function changeLanguage(language: Language) {
    if (!data || language === data.language) return;
    try {
      await updateSettings({ language });
      document.cookie = `locale=${language};path=/;max-age=31536000;samesite=lax`;
      window.location.reload(); // re-render with the new locale
    } catch {
      setError(t("saveError"));
    }
  }

  if (error && !data) {
    return <div className="p-6 text-sm text-red-500">{error}</div>;
  }
  if (!data) {
    return <div className="p-6 text-sm text-slate-400">…</div>;
  }

  return (
    <div className="mx-auto w-full max-w-2xl space-y-6 overflow-y-auto p-6">
      <div className="flex items-center justify-between">
        <p className="text-sm text-slate-500 dark:text-slate-400">{t("subtitle")}</p>
        {savedHint && <span className="text-xs font-medium text-emerald-500">{savedHint}</span>}
      </div>

      {/* Tab navigation */}
      <div className="flex gap-1 border-b border-slate-200 dark:border-slate-800">
        {TABS.map((key) => {
          const active = tab === key;
          return (
            <button
              key={key}
              type="button"
              onClick={() => setTab(key)}
              aria-current={active ? "page" : undefined}
              className={`-mb-px border-b-2 px-3 py-2 text-sm font-medium transition ${
                active
                  ? "border-brand-blue text-brand-blue"
                  : "border-transparent text-slate-500 hover:text-slate-800 dark:text-slate-400 dark:hover:text-slate-200"
              }`}
            >
              {t(key)}
            </button>
          );
        })}
      </div>

      {/* Tab panels */}
      <div className="space-y-4">
        {tab === "profile" && (
          <>
            <Row label={t("displayName")}>
              <div className="flex gap-2">
                <input className={fieldClass} value={name} onChange={(e) => setName(e.target.value)} />
                <button
                  type="button"
                  onClick={saveName}
                  disabled={savingName || name.trim() === data.display_name || !name.trim()}
                  className="grad shrink-0 rounded-lg px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-40"
                >
                  {t("save")}
                </button>
              </div>
            </Row>
            <Row label={t("email")}>
              <input className={`${fieldClass} opacity-60`} value={data.email} readOnly />
            </Row>
          </>
        )}

        {tab === "appearance" && (
          <>
            <Row label={t("language")}>
              <select
                className={fieldClass}
                value={data.language}
                onChange={(e) => changeLanguage(e.target.value as Language)}
              >
                <option value="de">Deutsch</option>
                <option value="en">English</option>
              </select>
            </Row>
            <Row label={t("theme")}>
              <select
                className={fieldClass}
                value={data.theme}
                onChange={(e) => changeTheme(e.target.value as Theme)}
              >
                <option value="dark">{t("themeDark")}</option>
                <option value="light">{t("themeLight")}</option>
                <option value="system">{t("themeSystem")}</option>
              </select>
            </Row>
          </>
        )}

        {tab === "agent" && <AgentTab />}

        {tab === "models" && <ModelsTab />}

        {tab === "connection" && (
          <Row label={t("connectionDefault")}>
            <select
              className={fieldClass}
              value={data.connection_default}
              onChange={(e) => changeConnection(e.target.value as ConnectionDefault)}
            >
              <option value="local">{t("connLocal")}</option>
              <option value="remote">{t("connRemote")}</option>
            </select>
          </Row>
        )}
      </div>

      {error && <p className="text-sm text-red-500">{error}</p>}
    </div>
  );
}
