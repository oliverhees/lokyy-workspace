"use client";

import { useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";

import { streamChat, type ChatMessage } from "@/lib/api";
import { ChatInput } from "./ChatInput";
import { EmptyState } from "./EmptyState";
import { MessageBubble } from "./MessageBubble";

// Optional local echo fallback for visual checks while the backend `/chat`
// endpoint does not exist yet. Off by default; enable with
// NEXT_PUBLIC_CHAT_ECHO=1 in the environment.
const ECHO_FALLBACK = process.env.NEXT_PUBLIC_CHAT_ECHO === "1";

export function Chat() {
  const t = useTranslations("chat");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streaming]);

  async function send(text: string) {
    setError(null);
    const history: ChatMessage[] = [...messages, { role: "user", content: text }];
    // Append the user message + an empty assistant placeholder we stream into.
    setMessages([...history, { role: "assistant", content: "" }]);
    setStreaming(true);

    const appendDelta = (delta: string) =>
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last && last.role === "assistant") {
          next[next.length - 1] = { ...last, content: last.content + delta };
        }
        return next;
      });

    try {
      await streamChat({ messages: history, onDelta: appendDelta });
    } catch {
      if (ECHO_FALLBACK) {
        // Simple local echo so the UI can be visually verified offline.
        const reply = `${t("echoPrefix")} ${text}`;
        for (const ch of reply) {
          appendDelta(ch);
          await new Promise((r) => setTimeout(r, 12));
        }
      } else {
        setError(t("error"));
        // Drop the empty assistant placeholder on failure.
        setMessages((prev) => {
          const next = [...prev];
          const last = next[next.length - 1];
          if (last && last.role === "assistant" && last.content === "") next.pop();
          return next;
        });
      }
    } finally {
      setStreaming(false);
    }
  }

  const isEmpty = messages.length === 0;

  return (
    <div className="flex min-h-0 flex-1 flex-col">
      <div ref={scrollRef} className="flex min-h-0 flex-1 flex-col overflow-y-auto">
        {isEmpty ? (
          <EmptyState />
        ) : (
          <div className="mx-auto flex w-full max-w-3xl flex-col gap-3 px-4 py-6">
            {messages.map((m, i) => (
              <MessageBubble
                key={i}
                message={m}
                pending={streaming && i === messages.length - 1 && m.role === "assistant"}
              />
            ))}
          </div>
        )}
      </div>

      {error && (
        <div className="mx-auto w-full max-w-3xl px-4 pb-1">
          <p className="rounded-lg border border-amber-300 bg-amber-50 px-3 py-2 text-xs text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
            {error}
          </p>
        </div>
      )}

      <ChatInput onSend={send} disabled={streaming} />
    </div>
  );
}
