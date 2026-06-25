// Agent context API (M2.1): the workspace persona (soul) + user profile that shape
// the chat system prompt.
import { apiFetch } from "./api";

export interface AgentContext {
  soul: string;
  user_profile: string;
  telos: string;
}

export async function fetchContext(): Promise<AgentContext> {
  const res = await apiFetch("/context");
  if (!res.ok) throw new Error(`context load failed: ${res.status}`);
  return (await res.json()) as AgentContext;
}

export async function updateContext(patch: Partial<AgentContext>): Promise<AgentContext> {
  const res = await apiFetch("/context", {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`context update failed: ${res.status}`);
  return (await res.json()) as AgentContext;
}
