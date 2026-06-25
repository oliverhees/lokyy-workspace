"use client";

// F4 — model endpoints management (rendered as the "Modelle" tab in settings).
// Model-agnostic: any OpenAI-compatible or Anthropic endpoint. API keys are
// write-only (server returns has_api_key only), so editing shows a key field that
// is left blank unless the user wants to replace/clear it.
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import {
  type ModelEndpoint,
  type ModelInput,
  type Provider,
  createModel,
  deleteModel,
  discoverModels,
  listModels,
  setDefaultModel,
  updateModel,
} from "@/lib/models";
import { PROVIDER_PRESETS, presetFor } from "@/lib/providers";
import { ModelCombobox } from "./ModelCombobox";

const fieldClass =
  "w-full rounded-lg border border-slate-300 bg-white px-3 py-1.5 text-sm outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/30 dark:border-slate-700 dark:bg-slate-900";

const emptyForm: ModelInput = {
  name: "",
  provider: "openai",
  base_url: "",
  model: "",
  api_key: "",
  is_default: false,
};

export function ModelsTab() {
  const t = useTranslations("models");
  const [items, setItems] = useState<ModelEndpoint[]>([]);
  const [editing, setEditing] = useState<string | "new" | null>(null);
  const [form, setForm] = useState<ModelInput>(emptyForm);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [discovered, setDiscovered] = useState<string[]>([]);
  const [discovering, setDiscovering] = useState(false);

  async function reload() {
    try {
      setItems(await listModels());
    } catch {
      setError(t("loadError"));
    }
  }

  useEffect(() => {
    reload();
    // eslint-disable-next-line react-hooks/exhaustive-deps
  }, []);

  function startNew() {
    // default to the first preset (OpenRouter) so the base URL is prefilled
    const p = PROVIDER_PRESETS[0];
    setForm({ ...emptyForm, provider: p.id, base_url: p.baseUrl });
    setDiscovered([]);
    setEditing("new");
    setError(null);
  }

  function pickProvider(id: string) {
    const p = presetFor(id);
    setDiscovered([]); // model list depends on the provider
    // prefill base URL from the preset, but don't clobber a URL the user typed
    setForm((f) => ({
      ...f,
      provider: (p?.id ?? id) as typeof f.provider,
      base_url: p && (!f.base_url || PROVIDER_PRESETS.some((x) => x.baseUrl === f.base_url))
        ? p.baseUrl
        : f.base_url,
    }));
  }

  async function loadModels() {
    setDiscovering(true);
    setError(null);
    try {
      const models = await discoverModels({
        provider: form.provider,
        base_url: form.base_url,
        api_key: form.api_key,
      });
      setDiscovered(models);
      if (models.length === 0) setError(t("noModelsFound"));
    } catch (e) {
      setError(e instanceof Error ? e.message : t("discoverError"));
    } finally {
      setDiscovering(false);
    }
  }

  function startEdit(ep: ModelEndpoint) {
    // key stays blank — only sent if the user types a new one
    setForm({ name: ep.name, provider: ep.provider, base_url: ep.base_url, model: ep.model, api_key: "" });
    setDiscovered([]);
    setEditing(ep.id);
    setError(null);
  }

  async function save() {
    setBusy(true);
    setError(null);
    try {
      if (editing === "new") {
        await createModel(form);
      } else if (editing) {
        // omit api_key when blank → leave unchanged
        const patch: Partial<ModelInput> = { ...form };
        if (!form.api_key) delete patch.api_key;
        await updateModel(editing, patch);
      }
      setEditing(null);
      await reload();
    } catch {
      setError(t("saveError"));
    } finally {
      setBusy(false);
    }
  }

  async function makeDefault(id: string) {
    await setDefaultModel(id);
    await reload();
  }

  async function remove(id: string) {
    await deleteModel(id);
    await reload();
  }

  if (editing !== null) {
    return (
      <div className="space-y-3">
        <h3 className="text-sm font-semibold text-slate-700 dark:text-slate-200">
          {editing === "new" ? t("addTitle") : t("editTitle")}
        </h3>
        <input className={fieldClass} placeholder={t("name")} value={form.name}
               onChange={(e) => setForm({ ...form, name: e.target.value })} />
        <select className={fieldClass} value={form.provider}
                onChange={(e) => pickProvider(e.target.value)}>
          {PROVIDER_PRESETS.map((p) => (
            <option key={p.id} value={p.id}>{p.label}</option>
          ))}
        </select>
        <input className={fieldClass} placeholder={t("baseUrl")} value={form.base_url}
               onChange={(e) => setForm({ ...form, base_url: e.target.value })} />
        <input className={fieldClass} type="password" autoComplete="off"
               placeholder={editing === "new" ? t("apiKey") : t("apiKeyKeep")} value={form.api_key}
               onChange={(e) => setForm({ ...form, api_key: e.target.value })} />

        <div className="flex items-start gap-2">
          <ModelCombobox
            value={form.model}
            onChange={(m) => setForm({ ...form, model: m })}
            options={discovered}
            placeholder={presetFor(form.provider)?.modelHint ?? t("model")}
          />
          {form.base_url && (
            <button
              type="button"
              onClick={loadModels}
              disabled={discovering}
              className="shrink-0 rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium disabled:opacity-50 dark:border-slate-700"
            >
              {discovering ? t("loadingModels") : t("loadModels")}
            </button>
          )}
        </div>
        {discovered.length > 0 && (
          <p className="text-xs text-slate-400">{t("modelsFound", { count: discovered.length })}</p>
        )}

        {error && <p className="text-sm text-red-500">{error}</p>}

        <div className="flex gap-2">
          <button type="button" onClick={save}
                  disabled={busy || !form.name.trim() || !form.model.trim()}
                  className="grad rounded-lg px-3 py-1.5 text-sm font-semibold text-white disabled:opacity-40">
            {t("save")}
          </button>
          <button type="button" onClick={() => setEditing(null)}
                  className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium dark:border-slate-700">
            {t("cancel")}
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="space-y-3">
      {items.length === 0 && (
        <p className="text-sm text-slate-500 dark:text-slate-400">{t("empty")}</p>
      )}

      {items.map((ep) => (
        <div key={ep.id}
             className="flex items-center justify-between rounded-lg border border-slate-200 bg-white px-4 py-3 dark:border-slate-800 dark:bg-slate-950">
          <div className="min-w-0">
            <div className="flex items-center gap-2">
              <span className="truncate text-sm font-medium text-slate-800 dark:text-slate-100">{ep.name}</span>
              {ep.is_default && (
                <span className="grad rounded-full px-2 py-0.5 text-[10px] font-semibold text-white">{t("default")}</span>
              )}
              {ep.has_api_key && (
                <span className="rounded-full border border-slate-200 px-2 py-0.5 text-[10px] text-slate-400 dark:border-slate-700">{t("keySet")}</span>
              )}
            </div>
            <p className="truncate text-xs text-slate-500 dark:text-slate-400">
              {ep.provider} · {ep.model} · {ep.base_url}
            </p>
          </div>
          <div className="flex shrink-0 items-center gap-1.5">
            {!ep.is_default && (
              <button type="button" onClick={() => makeDefault(ep.id)}
                      className="rounded-lg border border-slate-300 px-2.5 py-1 text-xs font-medium dark:border-slate-700">
                {t("makeDefault")}
              </button>
            )}
            <button type="button" onClick={() => startEdit(ep)}
                    className="rounded-lg border border-slate-300 px-2.5 py-1 text-xs font-medium dark:border-slate-700">
              {t("edit")}
            </button>
            <button type="button" onClick={() => remove(ep.id)}
                    className="rounded-lg border border-red-300 px-2.5 py-1 text-xs font-medium text-red-600 dark:border-red-500/40 dark:text-red-400">
              {t("delete")}
            </button>
          </div>
        </div>
      ))}

      {error && <p className="text-sm text-red-500">{error}</p>}

      <button type="button" onClick={startNew}
              className="grad rounded-lg px-3 py-1.5 text-sm font-semibold text-white">
        {t("add")}
      </button>
    </div>
  );
}
