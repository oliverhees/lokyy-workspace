"use client";

// F5/F5.1 — chat bound to a persisted session. Loads history, streams the reply
// from the real model, shows a phase indicator (connecting → thinking → writing)
// and a model · time caption under each answer.
import { useTranslations } from "next-intl";
import { useEffect, useRef, useState } from "react";

import { streamChat, type ChatMessage } from "@/lib/api";
import { listModels, type ModelEndpoint } from "@/lib/models";
import { getMessages } from "@/lib/sessions";
import { ChatInput } from "./ChatInput";
import { EmptyState } from "./EmptyState";
import { MessageBubble, type ChatPhase } from "./MessageBubble";

export function Chat({ sessionId, onActivity }: { sessionId: string; onActivity?: () => void }) {
  const t = useTranslations("chat");
  const [messages, setMessages] = useState<ChatMessage[]>([]);
  const [streaming, setStreaming] = useState(false);
  const [phase, setPhase] = useState<ChatPhase>(null);
  const [error, setError] = useState<string | null>(null);
  const [models, setModels] = useState<ModelEndpoint[]>([]);
  const [activeModelId, setActiveModelId] = useState<string | null>(null);
  const scrollRef = useRef<HTMLDivElement>(null);

  // Load the session's persisted history whenever the active session changes.
  useEffect(() => {
    let active = true;
    setError(null);
    getMessages(sessionId)
      .then((m) => active && setMessages(m))
      .catch(() => active && setMessages([]));
    return () => {
      active = false;
    };
  }, [sessionId]);

  // Load configured models so the user can switch per conversation; preselect default.
  useEffect(() => {
    let active = true;
    listModels()
      .then((ms) => {
        if (!active) return;
        setModels(ms);
        setActiveModelId((cur) => cur ?? ms.find((m) => m.is_default)?.id ?? ms[0]?.id ?? null);
      })
      .catch(() => {});
    return () => {
      active = false;
    };
  }, []);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, streaming]);

  async function send(text: string) {
    setError(null);
    const history: ChatMessage[] = [...messages, { role: "user", content: text }];
    setMessages([...history, { role: "assistant", content: "" }]);
    setStreaming(true);
    setPhase("connecting");

    // escalate to "thinking" if the first token is slow to arrive
    const thinkTimer = setTimeout(() => setPhase((p) => (p === "connecting" ? "thinking" : p)), 700);

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
      await streamChat({
        sessionId,
        content: text,
        modelEndpointId: activeModelId,
        onDelta: (d) => {
          setPhase("writing");
          appendDelta(d);
        },
      });
      // stamp the freshly completed answer with model + time for its caption
      const usedModel = models.find((m) => m.id === activeModelId)?.model ?? null;
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last && last.role === "assistant") {
          next[next.length - 1] = {
            ...last,
            model_used: usedModel,
            created_at: new Date().toISOString(),
          };
        }
        return next;
      });
      onActivity?.();
    } catch {
      setError(t("error"));
      setMessages((prev) => {
        const next = [...prev];
        const last = next[next.length - 1];
        if (last && last.role === "assistant" && last.content === "") next.pop();
        return next;
      });
    } finally {
      clearTimeout(thinkTimer);
      setStreaming(false);
      setPhase(null);
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
                phase={phase}
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

      <ChatInput
        onSend={send}
        disabled={streaming}
        models={models}
        activeModelId={activeModelId}
        onSelectModel={setActiveModelId}
      />
    </div>
  );
}
