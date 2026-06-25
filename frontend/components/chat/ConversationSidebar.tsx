"use client";

// F5 — conversation list for the chat. New / switch / delete persisted sessions.
import { useTranslations } from "next-intl";

import type { ChatSession } from "@/lib/sessions";

interface Props {
  sessions: ChatSession[];
  activeId: string | null;
  onSelect: (id: string) => void;
  onNew: () => void;
  onDelete: (id: string) => void;
}

export function ConversationSidebar({ sessions, activeId, onSelect, onNew, onDelete }: Props) {
  const t = useTranslations("chat");

  return (
    <aside className="flex w-60 shrink-0 flex-col border-r border-slate-200 bg-white dark:border-slate-800 dark:bg-slate-950">
      <div className="p-3">
        <button
          type="button"
          onClick={onNew}
          className="grad w-full rounded-lg px-3 py-1.5 text-sm font-semibold text-white"
        >
          {t("newChat")}
        </button>
      </div>
      <div className="min-h-0 flex-1 overflow-y-auto px-2 pb-2">
        {sessions.length === 0 && (
          <p className="px-2 py-3 text-xs text-slate-400">{t("noConversations")}</p>
        )}
        {sessions.map((s) => {
          const active = s.id === activeId;
          return (
            <div
              key={s.id}
              className={`group flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm ${
                active
                  ? "bg-slate-100 dark:bg-slate-800"
                  : "hover:bg-slate-50 dark:hover:bg-slate-900"
              }`}
            >
              <button
                type="button"
                onClick={() => onSelect(s.id)}
                className="min-w-0 flex-1 truncate text-left text-slate-700 dark:text-slate-300"
                title={s.title}
              >
                {s.title}
              </button>
              <button
                type="button"
                onClick={() => onDelete(s.id)}
                aria-label={t("delete")}
                className="shrink-0 rounded px-1 text-xs text-slate-400 opacity-0 transition hover:text-red-500 group-hover:opacity-100"
              >
                ✕
              </button>
            </div>
          );
        })}
      </div>
    </aside>
  );
}
