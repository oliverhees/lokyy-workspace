import type { ChatMessage } from "@/lib/api";

// A single chat bubble. User messages use the brand Cyan→Blue gradient
// (right-aligned); assistant messages are a clean surface (left-aligned).
export function MessageBubble({ message, pending }: { message: ChatMessage; pending?: boolean }) {
  const isUser = message.role === "user";
  return (
    <div className={`flex w-full ${isUser ? "justify-end" : "justify-start"}`}>
      <div
        className={
          isUser
            ? "grad max-w-[80%] whitespace-pre-wrap break-words rounded-2xl rounded-br-sm px-4 py-2.5 text-sm text-white shadow-sm"
            : "max-w-[80%] whitespace-pre-wrap break-words rounded-2xl rounded-bl-sm border border-slate-200 bg-white px-4 py-2.5 text-sm text-slate-800 shadow-sm dark:border-slate-700 dark:bg-slate-800 dark:text-slate-100"
        }
      >
        {message.content}
        {pending && (
          <span className="ml-0.5 inline-block h-3.5 w-1.5 animate-pulse rounded-sm bg-current align-middle opacity-70" />
        )}
      </div>
    </div>
  );
}
