"use client";

import { useTranslations } from "next-intl";
import { useEffect, useState } from "react";

import { checkHealth } from "@/lib/api";
import { apiBaseFor, getMode, hasRemote, setMode, type ConnMode } from "@/lib/connection";

export function ConnectionSwitch() {
  const t = useTranslations("conn");
  const [mode, setLocalMode] = useState<ConnMode>("local");
  const [online, setOnline] = useState<boolean | null>(null);
  const remoteAvailable = hasRemote();

  useEffect(() => {
    setLocalMode(getMode());
  }, []);

  useEffect(() => {
    let active = true;
    setOnline(null);
    checkHealth(apiBaseFor(mode)).then((ok) => {
      if (active) setOnline(ok);
    });
    return () => {
      active = false;
    };
  }, [mode]);

  function choose(m: ConnMode) {
    setMode(m);
    setLocalMode(m);
  }

  const dot = online === null ? "bg-slate-400" : online ? "bg-emerald-500" : "bg-red-500";
  const label = online === null ? t("checking") : online ? t("connected") : t("offline");

  return (
    <div className="flex items-center gap-2">
      <span className="flex items-center gap-1.5 text-xs text-slate-500 dark:text-slate-400">
        <span className={`h-1.5 w-1.5 rounded-full ${dot}`} /> {label}
      </span>
      <div className="flex overflow-hidden rounded-lg border border-slate-300 text-xs dark:border-slate-700">
        <button
          onClick={() => choose("local")}
          className={mode === "local" ? "grad px-2.5 py-1.5 font-semibold text-white" : "px-2.5 py-1.5 text-slate-500"}
        >
          {t("local")}
        </button>
        <button
          onClick={() => choose("remote")}
          disabled={!remoteAvailable}
          title={remoteAvailable ? "" : t("noServer")}
          className={
            mode === "remote"
              ? "grad px-2.5 py-1.5 font-semibold text-white"
              : "px-2.5 py-1.5 text-slate-500 disabled:opacity-40"
          }
        >
          {t("remote")}
        </button>
      </div>
    </div>
  );
}
