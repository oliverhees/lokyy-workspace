"use client";

import { useEffect, useRef, useState } from "react";
import { useTranslations } from "next-intl";

import type { ModelEndpoint } from "@/lib/models";

// Small click-outside popover hook for the input-bar menus.
function usePopover() {
  const [open, setOpen] = useState(false);
  const ref = useRef<HTMLDivElement>(null);
  useEffect(() => {
    function onDown(e: MouseEvent) {
      if (ref.current && !ref.current.contains(e.target as Node)) setOpen(false);
    }
    document.addEventListener("mousedown", onDown);
    return () => document.removeEventListener("mousedown", onDown);
  }, []);
  return { open, setOpen, ref };
}

const pillClass =
  "flex items-center gap-1.5 rounded-lg border border-slate-300 px-2.5 py-1 text-xs font-medium text-slate-600 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800";

// ── "+" actions menu (files/skills/MCP) — preview, wired up with their milestones ──
function PlusMenu() {
  const t = useTranslations("chat");
  const { open, setOpen, ref } = usePopover();
  const items = [
    { key: "addFiles", soon: true },
    { key: "skills", soon: true },
    { key: "mcp", soon: true },
  ];
  return (
    <div ref={ref} className="relative">
      <button
        type="button"
        onClick={() => setOpen((o) => !o)}
        aria-label={t("addActions")}
        className="flex h-7 w-7 items-center justify-center rounded-lg border border-slate-300 text-slate-500 transition hover:bg-slate-100 dark:border-slate-700 dark:text-slate-300 dark:hover:bg-slate-800"
      >
        +
      </button>
      {open && (
        <ul className="absolute bottom-full left-0 z-30 mb-1 w-56 rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-900">
          {items.map((it) => (
            <li key={it.key}>
              <span
                aria-disabled="true"
                className="flex cursor-not-allowed items-center justify-between px-3 py-1.5 text-xs text-slate-400 dark:text-slate-500"
              >
                {t(it.key)}
                <span className="rounded bg-slate-100 px-1.5 py-0.5 text-[10px] dark:bg-slate-800">
                  {t("soon")}
                </span>
              </span>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Model picker — fully functional: switch model per conversation ──
function ModelPicker({
  models,
  activeId,
  onSelect,
}: {
  models: ModelEndpoint[];
  activeId: string | null;
  onSelect: (id: string) => void;
}) {
  const t = useTranslations("chat");
  const { open, setOpen, ref } = usePopover();
  if (models.length === 0) return <span className="text-xs text-slate-400">{t("noModel")}</span>;
  const active = models.find((m) => m.id === activeId) ?? models.find((m) => m.is_default) ?? models[0];

  // group by provider (like the reference UI)
  const groups = models.reduce<Record<string, ModelEndpoint[]>>((acc, m) => {
    (acc[m.provider] ??= []).push(m);
    return acc;
  }, {});

  return (
    <div ref={ref} className="relative">
      <button type="button" onClick={() => setOpen((o) => !o)} className={pillClass}>
        <span className="grad-text font-semibold">◆</span>
        <span className="max-w-[12rem] truncate">{active?.model}</span>
        <span className="text-slate-400">▾</span>
      </button>
      {open && (
        <ul className="absolute bottom-full left-0 z-30 mb-1 max-h-72 w-72 overflow-y-auto rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-900">
          {Object.entries(groups).map(([provider, ms]) => (
            <li key={provider}>
              <p className="px-3 pb-0.5 pt-2 text-[10px] uppercase tracking-wide text-slate-400">
                {provider}
              </p>
              {ms.map((m) => (
                <button
                  key={m.id}
                  type="button"
                  onClick={() => {
                    onSelect(m.id);
                    setOpen(false);
                  }}
                  className={`block w-full truncate px-3 py-1.5 text-left text-xs hover:bg-slate-100 dark:hover:bg-slate-800 ${
                    m.id === active?.id ? "text-brand-blue" : "text-slate-700 dark:text-slate-300"
                  }`}
                >
                  {m.model}
                </button>
              ))}
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// ── Agent mode picker — preview; takes effect with the agent loop (M2/M4) ──
function ModePicker() {
  const t = useTranslations("chat");
  const { open, setOpen, ref } = usePopover();
  const modes = ["modeStandard", "modeAuto", "modeYolo"] as const;
  const [mode, setMode] = useState<(typeof modes)[number]>("modeStandard");
  return (
    <div ref={ref} className="relative">
      <button type="button" onClick={() => setOpen((o) => !o)} className={pillClass}>
        <span>🛡</span>
        <span>{t(mode)}</span>
        <span className="text-slate-400">▾</span>
      </button>
      {open && (
        <ul className="absolute bottom-full left-0 z-30 mb-1 w-56 rounded-lg border border-slate-200 bg-white py-1 shadow-lg dark:border-slate-700 dark:bg-slate-900">
          <li className="px-3 pb-0.5 pt-1 text-[10px] uppercase tracking-wide text-slate-400">
            {t("switchMode")} · {t("soon")}
          </li>
          {modes.map((m) => (
            <li key={m}>
              <button
                type="button"
                onClick={() => {
                  setMode(m);
                  setOpen(false);
                }}
                className={`block w-full px-3 py-1.5 text-left text-xs hover:bg-slate-100 dark:hover:bg-slate-800 ${
                  m === mode ? "text-brand-blue" : "text-slate-700 dark:text-slate-300"
                }`}
              >
                {m === mode ? "✓ " : ""}
                {t(m)}
              </button>
            </li>
          ))}
        </ul>
      )}
    </div>
  );
}

// Multiline-aware input bar with model picker (functional) + previews of the
// upcoming actions (files/skills/MCP, mode, voice). Enter sends, Shift+Enter newline.
export function ChatInput({
  onSend,
  disabled,
  models = [],
  activeModelId = null,
  onSelectModel,
}: {
  onSend: (text: string) => void;
  disabled?: boolean;
  models?: ModelEndpoint[];
  activeModelId?: string | null;
  onSelectModel?: (id: string) => void;
}) {
  const t = useTranslations("chat");
  const [value, setValue] = useState("");
  const ref = useRef<HTMLTextAreaElement>(null);

  function submit() {
    const text = value.trim();
    if (!text || disabled) return;
    onSend(text);
    setValue("");
    if (ref.current) ref.current.style.height = "auto";
  }

  function onKeyDown(e: React.KeyboardEvent<HTMLTextAreaElement>) {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      submit();
    }
  }

  function autoGrow(el: HTMLTextAreaElement) {
    el.style.height = "auto";
    el.style.height = `${Math.min(el.scrollHeight, 160)}px`;
  }

  return (
    <div className="border-t border-slate-200 bg-slate-50 p-3 dark:border-slate-800 dark:bg-navy">
      <div className="mx-auto max-w-3xl rounded-2xl border border-slate-300 bg-white px-3 pb-2 pt-2.5 shadow-sm focus-within:border-brand-blue focus-within:ring-2 focus-within:ring-brand-blue/20 dark:border-slate-700 dark:bg-slate-800">
        <textarea
          ref={ref}
          rows={1}
          value={value}
          placeholder={t("placeholderFull")}
          aria-label={t("placeholderFull")}
          onChange={(e) => {
            setValue(e.target.value);
            autoGrow(e.target);
          }}
          onKeyDown={onKeyDown}
          className="w-full resize-none bg-transparent px-1 text-sm text-slate-900 outline-none placeholder:text-slate-400 dark:text-slate-100"
        />
        <div className="mt-1.5 flex items-center gap-2">
          <PlusMenu />
          <div className="flex-1" />
          {onSelectModel && (
            <ModelPicker models={models} activeId={activeModelId} onSelect={onSelectModel} />
          )}
          <ModePicker />
          <button
            type="button"
            disabled
            aria-label={t("voice")}
            title={`${t("voice")} · ${t("soon")}`}
            className="flex h-7 w-7 cursor-not-allowed items-center justify-center rounded-lg text-slate-400"
          >
            🎤
          </button>
          <button
            onClick={submit}
            disabled={disabled || value.trim().length === 0}
            aria-label={t("send")}
            className="grad flex h-8 w-8 shrink-0 items-center justify-center rounded-full text-white transition-opacity disabled:cursor-not-allowed disabled:opacity-40"
          >
            ↑
          </button>
        </div>
      </div>
      <p className="mx-auto mt-1.5 max-w-3xl px-1 text-[11px] text-slate-400 dark:text-slate-500">
        📁 {t("workInProject")} · {t("soon")}
      </p>
    </div>
  );
}
