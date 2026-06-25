// Provider presets (F4.1). Keep ids in sync with backend KNOWN_PROVIDERS (llm.py).
// Selecting a preset prefills the base URL. OpenRouter is listed first — one key,
// access to all major models. "custom" covers any self-hosted OpenAI-API endpoint.
import type { Provider } from "./models";

export interface ProviderPreset {
  id: Provider;
  label: string;
  /** Prefilled base URL. Empty = LiteLLM uses the provider default (native). */
  baseUrl: string;
  /** Hint about the model id field. */
  modelHint: string;
}

export const PROVIDER_PRESETS: ProviderPreset[] = [
  { id: "openrouter", label: "OpenRouter — alle großen Modelle", baseUrl: "https://openrouter.ai/api/v1", modelHint: "z. B. anthropic/claude-sonnet-4" },
  { id: "openai", label: "OpenAI", baseUrl: "https://api.openai.com/v1", modelHint: "z. B. gpt-5" },
  { id: "anthropic", label: "Anthropic", baseUrl: "", modelHint: "z. B. claude-sonnet-4" },
  { id: "gemini", label: "Google Gemini", baseUrl: "", modelHint: "z. B. gemini-2.5-pro" },
  { id: "groq", label: "Groq", baseUrl: "https://api.groq.com/openai/v1", modelHint: "z. B. llama-3.3-70b" },
  { id: "mistral", label: "Mistral", baseUrl: "https://api.mistral.ai/v1", modelHint: "z. B. mistral-large-latest" },
  { id: "deepseek", label: "DeepSeek", baseUrl: "https://api.deepseek.com/v1", modelHint: "z. B. deepseek-chat" },
  { id: "together_ai", label: "Together AI", baseUrl: "https://api.together.xyz/v1", modelHint: "Modell-ID" },
  { id: "ollama", label: "Ollama (lokal)", baseUrl: "http://localhost:11434", modelHint: "z. B. llama3.1" },
  { id: "custom", label: "Eigene / OpenAI-kompatibel", baseUrl: "", modelHint: "Modell-ID deines Endpoints" },
];

export function presetFor(id: string): ProviderPreset | undefined {
  return PROVIDER_PRESETS.find((p) => p.id === id);
}
