"use client";

// F2 — authenticated app shell. Every feature page under (app) renders inside
// this frame: guarded by auth, with the persistent sidebar + top bar.
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";

import { RequireAuth } from "@/components/auth/RequireAuth";
import { Sidebar } from "@/components/shell/Sidebar";
import { Topbar } from "@/components/shell/Topbar";

function titleFor(pathname: string, t: (k: string) => string): string {
  if (pathname.startsWith("/chat")) return t("chat");
  if (pathname.startsWith("/dashboard")) return t("dashboard");
  if (pathname.startsWith("/settings")) return t("settings");
  return "";
}

export default function AppLayout({ children }: { children: React.ReactNode }) {
  const t = useTranslations("nav");
  const pathname = usePathname();
  return (
    <RequireAuth>
      <div className="flex h-screen">
        <Sidebar />
        <div className="flex min-w-0 flex-1 flex-col">
          <Topbar title={titleFor(pathname, t)} />
          <main className="min-h-0 flex-1 overflow-hidden">{children}</main>
        </div>
      </div>
    </RequireAuth>
  );
}
