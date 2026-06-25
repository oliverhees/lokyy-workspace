import { useTranslations } from "next-intl";
import Image from "next/image";

import { ConnectionSwitch } from "@/components/ConnectionSwitch";
import { LanguageSwitch } from "@/components/LanguageSwitch";

export default function Home() {
  const t = useTranslations("app");
  return (
    <main className="flex min-h-screen flex-col">
      <header className="flex h-14 shrink-0 items-center justify-between border-b border-slate-200 px-4 dark:border-slate-800">
        <div className="flex items-center gap-3">
          <Image src="/lokyy-logo.png" alt="Lokyy" width={32} height={32} priority />
          <span className="text-xl font-extrabold tracking-tight">
            lokyy<span className="grad-text"> workspace</span>
          </span>
          <span className="ml-2 rounded-full border border-slate-200 bg-slate-100 px-2 py-0.5 text-xs text-slate-500 dark:border-slate-700 dark:bg-slate-800 dark:text-slate-400">
            {t("badge")}
          </span>
        </div>
        <div className="flex items-center gap-2">
          <ConnectionSwitch />
          <LanguageSwitch />
        </div>
      </header>

      <section className="flex flex-1 flex-col items-center justify-center gap-6 px-6 text-center">
        <Image src="/lokyy-logo.png" alt="Lokyy" width={96} height={96} priority />
        <h1 className="text-3xl font-extrabold">
          lokyy<span className="grad-text"> workspace</span>
        </h1>
        <p className="max-w-md text-slate-500 dark:text-slate-400">{t("tagline")}</p>
        <span className="rounded-full border border-amber-300 bg-amber-50 px-3 py-1 text-xs font-medium text-amber-700 dark:border-amber-500/30 dark:bg-amber-500/10 dark:text-amber-300">
          {t("beta")}
        </span>
      </section>
    </main>
  );
}
