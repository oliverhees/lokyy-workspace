import { useTranslations } from "next-intl";
import Image from "next/image";

// Shown when there are no messages yet.
export function EmptyState() {
  const t = useTranslations("chat");
  return (
    <div className="flex flex-1 flex-col items-center justify-center gap-4 px-6 text-center">
      <Image src="/lokyy-logo.png" alt="Lokyy" width={72} height={72} priority />
      <h2 className="text-2xl font-extrabold">
        {t("emptyTitle")}
        <span className="grad-text"> workspace</span>
      </h2>
      <p className="max-w-sm text-sm text-slate-500 dark:text-slate-400">{t("empty")}</p>
    </div>
  );
}
