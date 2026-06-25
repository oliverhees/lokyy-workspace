"use client";

// F2 — App-Shell top bar: page title on the left, global controls on the right.
import { ConnectionSwitch } from "@/components/ConnectionSwitch";
import { LanguageSwitch } from "@/components/LanguageSwitch";
import { UserMenu } from "@/components/auth/UserMenu";

export function Topbar({ title }: { title?: string }) {
  return (
    <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
      <h1 className="text-sm font-semibold text-slate-700 dark:text-slate-200">{title}</h1>
      <div className="flex items-center gap-2">
        <ConnectionSwitch />
        <LanguageSwitch />
        <UserMenu />
      </div>
    </header>
  );
}
