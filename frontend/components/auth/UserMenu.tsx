"use client";

// F1 — current user + logout, shown in authenticated headers.
import { useRouter } from "next/navigation";
import { useTranslations } from "next-intl";

import { useAuth } from "./AuthProvider";

export function UserMenu() {
  const t = useTranslations("auth");
  const { user, logout } = useAuth();
  const router = useRouter();

  if (!user) return null;

  async function onLogout() {
    await logout();
    router.replace("/login");
  }

  return (
    <div className="flex items-center gap-2">
      <span
        className="hidden max-w-[12rem] truncate text-sm text-slate-600 sm:inline dark:text-slate-300"
        title={user.email}
      >
        {user.display_name}
      </span>
      <button
        type="button"
        onClick={onLogout}
        className="rounded-lg border border-slate-300 px-3 py-1.5 text-sm font-medium transition hover:bg-slate-100 dark:border-slate-700 dark:hover:bg-slate-800"
      >
        {t("logout")}
      </button>
    </div>
  );
}
