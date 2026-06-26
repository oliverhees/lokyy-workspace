// Projects API client (M3.1). A project is an owner-scoped folder in the workspace;
// `dirname` is the stable on-disk folder name, `name` the renameable display name.
import { apiFetch } from "./api";

export interface Project {
  id: string;
  name: string;
  dirname: string;
}

export async function listProjects(): Promise<Project[]> {
  const res = await apiFetch("/projects");
  if (!res.ok) throw new Error(`projects load failed: ${res.status}`);
  return (await res.json()) as Project[];
}

export async function createProject(name: string): Promise<Project> {
  const res = await apiFetch("/projects", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error(`project create failed: ${res.status}`);
  return (await res.json()) as Project;
}

export async function renameProject(id: string, name: string): Promise<Project> {
  const res = await apiFetch(`/projects/${id}`, {
    method: "PATCH",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify({ name }),
  });
  if (!res.ok) throw new Error(`project rename failed: ${res.status}`);
  return (await res.json()) as Project;
}

export async function deleteProject(id: string): Promise<void> {
  const res = await apiFetch(`/projects/${id}`, { method: "DELETE" });
  if (!res.ok && res.status !== 204) throw new Error(`project delete failed: ${res.status}`);
}
