import type { ChatMessage } from "@/lib/api";

export type ChatPhase = "connecting" | "thinking" | "writing" | null;

function formatTime(iso?: string): string {
  const d = iso ? new Date(iso) : new Date();
  return d.toLocaleTimeString("de-DE", { hour: "2-digit", minute: "2-digit" });
}

function PhaseIndicator({ phase }: { phase: ChatPhase }) {
  const label =
    phase === "connecting" ? "Verbinde …" : phase === "writing" ? "Schreibt …" : "Denkt nach …";
  return (
    <span className="flex items-center gap-2 text-slate-500 dark:text-slate-400">
      <span
        className="inline-block h-3.5 w-3.5 animate-spin rounded-full border-2 border-slate-300 border-t-brand-blue dark:border-slate-600 dark:border-t-brand-cyan"
        aria-hidden="true"
      />
      {label}
    </span>
  );
}

// A single chat bubble. User messages use the brand Cyan→Blue gradient
// (right-aligned); assistant messages are a clean surface (left-aligned) with a
// phase indicator while waiting and a model · time caption once answered.
export function MessageBubble({
  message,
  pending,
  phase,
}: {
  message: ChatMessage;
  pending?: boolean;
  phase?: ChatPhase;
}) {
  const isUser = message.role === "user";
  const showPhase = !!pending && !isUser && message.content.length === 0;
  const showCaption = !isUser && !pending && message.content.length > 0;

  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div className="flex max-w-[80%] flex-col gap-1">
        <div
          className={
            isUser
              ? "grad whitespace-pre-wrap break-words rounded-2xl rounded-br-sm px-4 py-2.5 text-sm text-white shadow-sm"
              : "whitespace-pre-wrap break-words rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-800 shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
          }
        >
          {showPhase ? (
            <PhaseIndicator phase={phase ?? "thinking"} />
          ) : (
            <>
              {message.content}
              {pending && (
                <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse rounded-sm bg-current align-middle opacity-70" />
              )}
            </>
          )}
        </div>
        {showCaption && (
          <span className="px-1 text-[11px] text-slate-400 dark:text-slate-500">
            {message.model_used ? `${message.model_used} · ` : ""}
            {formatTime(message.created_at)}
          </span>
        )}
      </div>
    </div>
  );
}
