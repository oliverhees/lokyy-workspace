// Minimal API client against the active backend (see connection.ts).
import { getApiBase } from "./connection";

export async function apiFetch(path: string, init?: RequestInit): Promise<Response> {
  return fetch(getApiBase() + path, { credentials: "include", ...init });
}

export async function checkHealth(base?: string): Promise<boolean> {
  try {
    const res = await fetch((base ?? getApiBase()) + "/health", { cache: "no-store" });
    if (!res.ok) return false;
    const data = (await res.json()) as { status?: string };
    return data.status === "ok";
  } catch {
    return false;
  }
}

// --- Chat (M1/T1.6) ---------------------------------------------------------
// The frontend talks to a (planned) backend endpoint `POST {apiBase}/chat`.
// The backend answers with an SSE stream of text deltas:
//   data: {"delta": "Hallo"}\n\n
//   data: {"delta": " Welt"}\n\n
//   data: [DONE]\n\n
// This client also tolerates a raw text/plain stream (each chunk = a delta),
// so the UI works against early/partial backends without changes.

export interface ChatMessage {
  role: "user" | "assistant";
  content: string;
}

export interface ChatStreamOptions {
  messages: ChatMessage[];
  signal?: AbortSignal;
  /** Called for every text delta as it arrives. */
  onDelta: (delta: string) => void;
}

/**
 * Streams an assistant reply from the backend `/chat` endpoint.
 * Throws if the connection fails or the server responds with a non-OK status
 * — callers should catch and surface a friendly hint (no crash).
 */
export async function streamChat({ messages, signal, onDelta }: ChatStreamOptions): Promise<void> {
  const res = await fetch(getApiBase() + "/chat", {
    method: "POST",
    credentials: "include",
    headers: { "Content-Type": "application/json", Accept: "text/event-stream" },
    body: JSON.stringify({ messages }),
    signal,
  });

  if (!res.ok || !res.body) {
    throw new Error(`chat request failed: ${res.status}`);
  }

  const reader = res.body.getReader();
  const decoder = new TextDecoder();
  let buffer = "";
  const contentType = res.headers.get("content-type") ?? "";
  const isSse = contentType.includes("text/event-stream");

  try {
    for (;;) {
      const { done, value } = await reader.read();
      if (done) break;
      const chunk = decoder.decode(value, { stream: true });

      if (!isSse) {
        // Plain text stream: every chunk is a delta.
        if (chunk) onDelta(chunk);
        continue;
      }

      buffer += chunk;
      // SSE events are separated by a blank line.
      let sep: number;
      while ((sep = buffer.indexOf("\n\n")) !== -1) {
        const rawEvent = buffer.slice(0, sep);
        buffer = buffer.slice(sep + 2);
        const delta = parseSseEvent(rawEvent);
        if (delta) onDelta(delta);
      }
    }
  } finally {
    reader.releaseLock();
  }
}

/** Extracts a text delta from a single SSE event block. Returns "" to skip. */
function parseSseEvent(rawEvent: string): string {
  let out = "";
  for (const line of rawEvent.split("\n")) {
    const trimmed = line.trimStart();
    if (!trimmed.startsWith("data:")) continue;
    const payload = trimmed.slice(5).trim();
    if (!payload || payload === "[DONE]") continue;
    try {
      const parsed = JSON.parse(payload) as { delta?: string; content?: string };
      out += parsed.delta ?? parsed.content ?? "";
    } catch {
      // Not JSON — treat the raw data payload as the delta itself.
      out += payload;
    }
  }
  return out;
}
