// Model endpoints API client (F4). Keys are write-only: the server never returns
// the plaintext key, only `has_api_key`. Sending api_key: "" clears it; omitting it
// on update leaves it unchanged.
import { apiFetch } from "./api";

export type Provider = "openai" | "anthropic";

export interface ModelEndpoint {
  id: string;
  name: string;
  provider: Provider;
  base_url: string;
  model: string;
  is_default: boolean;
  has_api_key: boolean;
}

export interface ModelInput {
  name: string;
  provider: Provider;
  base_url: string;
  model: string;
  api_key?: string;
  is_default?: boolean;
}

export async function listModels(): Promise<ModelEndpoint[]> {
  const res = await apiFetch("/models");
  if (!res.ok) throw new Error(`models load failed: ${res.status}`);
  return (await res.json()) as ModelEndpoint[];
}

export async function createModel(input: ModelInput): Promise<ModelEndpoint> {
  const res = await apiFetch("/models", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(input),
  });
  if (!res.ok) throw new Error(`model create failed: ${res.status}`);
  return (await res.json()) as ModelEndpoint;
}

export async function updateModel(id: string, patch: Partial<ModelInput>): Promise<ModelEndpoint> {
  const res = await apiFetch(`/models/${id}`, {
    method: "PUT",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(patch),
  });
  if (!res.ok) throw new Error(`model update failed: ${res.status}`);
  return (await res.json()) as ModelEndpoint;
}

export async function setDefaultModel(id: string): Promise<ModelEndpoint> {
  const res = await apiFetch(`/models/${id}/default`, { method: "POST" });
  if (!res.ok) throw new Error(`set default failed: ${res.status}`);
  return (await res.json()) as ModelEndpoint;
}

export async function deleteModel(id: string): Promise<void> {
  const res = await apiFetch(`/models/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) throw new Error(`model delete failed: ${res.status}`);
}
