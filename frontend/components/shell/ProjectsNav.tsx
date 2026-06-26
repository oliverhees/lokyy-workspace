"use client";

// M3.1 — projects section in the app sidebar: list + create + rename + delete.
// Each project is a real folder in the workspace, created server-side. Shown only
// in the expanded (sm+) sidebar. Deleting asks for confirmation (it removes the
// folder) — destructive actions are always confirmed.
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import {
  createProject,
  deleteProject,
  listProjects,
  renameProject,
  type Project,
} from "@/lib/projects";

const FolderIcon = () => (
  <svg
    width="16"
    height="16"
    viewBox="0 0 24 24"
    fill="none"
    stroke="currentColor"
    strokeWidth="2"
    strokeLinecap="round"
    strokeLinejoin="round"
    aria-hidden="true"
  >
    <path d="M3 7a2 2 0 0 1 2-2h4l2 2h8a2 2 0 0 1 2 2v8a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2z" />
  </svg>
);

export function ProjectsNav() {
  const t = useTranslations("projects");
  const [projects, setProjects] = useState<Project[]>([]);
  const [creating, setCreating] = useState(false);
  const [draft, setDraft] = useState("");
  const [editingId, setEditingId] = useState<string | null>(null);
  const [editName, setEditName] = useState("");

  useEffect(() => {
    listProjects()
      .then(setProjects)
      .catch(() => setProjects([]));
  }, []);

  async function handleCreate() {
    const name = draft.trim();
    setCreating(false);
    setDraft("");
    if (!name) return;
    try {
      const p = await createProject(name);
      setProjects((prev) => [...prev, p]);
    } catch {
      /* keep the UI alive; the list simply doesn't gain the project */
    }
  }

  async function handleRename(id: string) {
    const name = editName.trim();
    setEditingId(null);
    if (!name) return;
    try {
      const p = await renameProject(id, name);
      setProjects((prev) => prev.map((x) => (x.id === id ? p : x)));
    } catch {
      /* ignore — display name stays as it was */
    }
  }

  async function handleDelete(p: Project) {
    if (!window.confirm(t("confirmDelete", { name: p.name }))) return;
    try {
      await deleteProject(p.id);
      setProjects((prev) => prev.filter((x) => x.id !== p.id));
    } catch {
      /* ignore */
    }
  }

  return (
    <div className="mt-4 hidden min-h-0 flex-1 flex-col sm:flex">
      <div className="flex items-center justify-between px-3 pb-1">
        <span className="text-xs font-semibold uppercase tracking-wide text-slate-400">
          {t("title")}
        </span>
        <button
          type="button"
          onClick={() => {
            setCreating(true);
            setDraft("");
          }}
          aria-label={t("new")}
          title={t("new")}
          className="rounded px-1 text-lg leading-none text-slate-400 transition hover:text-slate-700 dark:hover:text-slate-200"
        >
          +
        </button>
      </div>

      <div className="min-h-0 flex-1 overflow-y-auto">
        {creating && (
          <input
            autoFocus
            value={draft}
            onChange={(e) => setDraft(e.target.value)}
            onKeyDown={(e) => {
              if (e.key === "Enter") handleCreate();
              if (e.key === "Escape") setCreating(false);
            }}
            onBlur={handleCreate}
            placeholder={t("namePlaceholder")}
            className="mx-2 mb-1 w-[calc(100%-1rem)] rounded border border-slate-300 bg-white px-2 py-1 text-sm dark:border-slate-700 dark:bg-slate-900"
          />
        )}
        {projects.length === 0 && !creating && (
          <p className="px-3 py-2 text-xs text-slate-400">{t("none")}</p>
        )}
        {projects.map((p) => (
          <div
            key={p.id}
            className="group flex items-center gap-1 rounded-lg px-2 py-1.5 text-sm hover:bg-slate-50 dark:hover:bg-slate-900"
          >
            <span className="shrink-0 text-slate-400">
              <FolderIcon />
            </span>
            {editingId === p.id ? (
              <input
                autoFocus
                value={editName}
                onChange={(e) => setEditName(e.target.value)}
                onKeyDown={(e) => {
                  if (e.key === "Enter") handleRename(p.id);
                  if (e.key === "Escape") setEditingId(null);
                }}
                onBlur={() => handleRename(p.id)}
                className="min-w-0 flex-1 rounded border border-slate-300 bg-white px-1 text-sm dark:border-slate-700 dark:bg-slate-900"
              />
            ) : (
              <button
                type="button"
                onDoubleClick={() => {
                  setEditingId(p.id);
                  setEditName(p.name);
                }}
                title={`${p.name} (${t("rename")}: Doppelklick)`}
                className="min-w-0 flex-1 truncate text-left text-slate-700 dark:text-slate-300"
              >
                {p.name}
              </button>
            )}
            <button
              type="button"
              onClick={() => handleDelete(p)}
              aria-label={t("delete")}
              className="shrink-0 rounded px-1 text-xs text-slate-400 opacity-0 transition hover:text-red-500 group-hover:opacity-100"
            >
              ✕
            </button>
          </div>
        ))}
      </div>
    </div>
  );
}
