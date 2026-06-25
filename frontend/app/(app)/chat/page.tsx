"use client";

// F5 — chat page: conversation sidebar + the active session's chat. Sessions and
// messages are persisted server-side, so reloading keeps the conversation.
import { useCallback, useEffect, useState } from "react";

import { Chat } from "@/components/chat/Chat";
import { ConversationSidebar } from "@/components/chat/ConversationSidebar";
import {
  type ChatSession,
  createSession,
  deleteSession,
  listSessions,
} from "@/lib/sessions";

export default function ChatPage() {
  const [sessions, setSessions] = useState<ChatSession[]>([]);
  const [activeId, setActiveId] = useState<string | null>(null);

  const refresh = useCallback(async () => {
    const list = await listSessions().catch(() => []);
    setSessions(list);
    return list;
  }, []);

  // On first load: show existing sessions, or create one so the user can start typing.
  useEffect(() => {
    let active = true;
    (async () => {
      let list = await listSessions().catch(() => []);
      if (list.length === 0) {
        try {
          list = [await createSession()];
        } catch {
          list = [];
        }
      }
      if (!active) return;
      setSessions(list);
      setActiveId((cur) => cur ?? list[0]?.id ?? null);
    })();
    return () => {
      active = false;
    };
  }, []);

  async function onNew() {
    const s = await createSession();
    setSessions((prev) => [s, ...prev]);
    setActiveId(s.id);
  }

  async function onDelete(id: string) {
    await deleteSession(id);
    const list = await refresh();
    if (activeId === id) {
      if (list.length) {
        setActiveId(list[0].id);
      } else {
        const s = await createSession();
        setSessions([s]);
        setActiveId(s.id);
      }
    }
  }

  return (
    <div className="flex h-full">
      <ConversationSidebar
        sessions={sessions}
        activeId={activeId}
        onSelect={setActiveId}
        onNew={onNew}
        onDelete={onDelete}
      />
      {activeId ? (
        <Chat key={activeId} sessionId={activeId} onActivity={refresh} />
      ) : (
        <div className="flex flex-1 items-center justify-center text-sm text-slate-400">…</div>
      )}
    </div>
  );
}
