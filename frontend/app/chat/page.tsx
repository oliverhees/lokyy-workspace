import { useTranslations } from "next-intl";
import Image from "next/image";
import Link from "next/link";

import { Chat } from "@/components/chat/Chat";
import { ConnectionSwitch } from "@/components/ConnectionSwitch";
import { LanguageSwitch } from "@/components/LanguageSwitch";

export default function ChatPage() {
  const t = useTranslations("app");
  return (
    <main className="flex h-screen flex-col">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
        <Link href="/" className="flex items-center gap-3">
          <Image src="/lokyy-logo.png" alt="Lokyy" width={32} height={32} priority />
          <span className="text-xl font-extrabold tracking-tight">
            lokyy<span className="grad-text"> workspace</span>
          </span>
          <span className="ml-2 rounded-full border border-slate-200 bg-slate-100 px-2 py-0.5 text-xs text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">
            {t("badge")}
          </span>
        </Link>
        <div className="flex items-center gap-2">
          <ConnectionSwitch />
          <LanguageSwitch />
        </div>
      </header>

      <Chat />
    </main>
  );
}
