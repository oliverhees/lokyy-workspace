// Chat sessions API client (F5). Sessions are owner-scoped; messages persist
// server-side so a conversation survives reloads and device switches.
import { apiFetch } from "./api";
import type { ChatMessage } from "./api";

export interface ChatSession {
  id: string;
  title: string;
}

export async function listSessions(): Promise<ChatSession[]> {
  const res = await apiFetch("/sessions");
  if (!res.ok) throw new Error(`sessions load failed: ${res.status}`);
  return (await res.json()) as ChatSession[];
}

export async function createSession(title?: string): Promise<ChatSession> {
  const res = await apiFetch("/sessions", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title: title ?? null }),
  });
  if (!res.ok) throw new Error(`session create failed: ${res.status}`);
  return (await res.json()) as ChatSession;
}

export async function getMessages(sessionId: string): Promise<ChatMessage[]> {
  const res = await apiFetch(`/sessions/${sessionId}/messages`);
  if (!res.ok) throw new Error(`messages load failed: ${res.status}`);
  return (await res.json()) as ChatMessage[];
}

export async function renameSession(sessionId: string, title: string): Promise<ChatSession> {
  const res = await apiFetch(`/sessions/${sessionId}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ title }),
  });
  if (!res.ok) throw new Error(`session rename failed: ${res.status}`);
  return (await res.json()) as ChatSession;
}

export async function deleteSession(sessionId: string): Promise<void> {
  const res = await apiFetch(`/sessions/${sessionId}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) throw new Error(`session delete failed: ${res.status}`);
}
