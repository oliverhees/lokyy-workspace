"use client";

// F2 — App-Shell navigation. The persistent left rail every feature hangs off.
// Items that aren't built yet are shown disabled with a "bald" hint so the
// shape of the product is visible without dead links.
import Image from "next/image";
import Link from "next/link";
import { usePathname } from "next/navigation";
import { useTranslations } from "next-intl";

function Svg({ children }: { children: React.ReactNode }) {
  return (
    <svg
      width="20"
      height="20"
      viewBox="0 0 24 24"
      fill="none"
      stroke="currentColor"
      strokeWidth="2"
      strokeLinecap="round"
      strokeLinejoin="round"
      aria-hidden="true"
    >
      {children}
    </svg>
  );
}

const ChatIcon = () => (
  <Svg>
    <path d="M21 15a2 2 0 0 1-2 2H7l-4 4V5a2 2 0 0 1 2-2h14a2 2 0 0 1 2 2z" />
  </Svg>
);

const DashboardIcon = () => (
  <Svg>
    <rect x="3" y="3" width="7" height="9" />
    <rect x="14" y="3" width="7" height="5" />
    <rect x="14" y="12" width="7" height="9" />
    <rect x="3" y="16" width="7" height="5" />
  </Svg>
);

const SettingsIcon = () => (
  <Svg>
    <circle cx="12" cy="12" r="3" />
    <path d="M19.4 15a1.65 1.65 0 0 0 .33 1.82l.06.06a2 2 0 1 1-2.83 2.83l-.06-.06a1.65 1.65 0 0 0-1.82-.33 1.65 1.65 0 0 0-1 1.51V21a2 2 0 0 1-4 0v-.09A1.65 1.65 0 0 0 9 19.4a1.65 1.65 0 0 0-1.82.33l-.06.06a2 2 0 1 1-2.83-2.83l.06-.06a1.65 1.65 0 0 0 .33-1.82 1.65 1.65 0 0 0-1.51-1H3a2 2 0 0 1 0-4h.09A1.65 1.65 0 0 0 4.6 9a1.65 1.65 0 0 0-.33-1.82l-.06-.06a2 2 0 1 1 2.83-2.83l.06.06a1.65 1.65 0 0 0 1.82.33H9a1.65 1.65 0 0 0 1-1.51V3a2 2 0 0 1 4 0v.09a1.65 1.65 0 0 0 1 1.51 1.65 1.65 0 0 0 1.82-.33l.06-.06a2 2 0 1 1 2.83 2.83l-.06.06a1.65 1.65 0 0 0-.33 1.82V9a1.65 1.65 0 0 0 1.51 1H21a2 2 0 0 1 0 4h-.09a1.65 1.65 0 0 0-1.51 1z" />
  </Svg>
);

interface NavItem {
  key: string;
  href: string;
  Icon: () => React.ReactElement;
  available: boolean;
}

const NAV: NavItem[] = [
  { key: "chat", href: "/chat", available: true, Icon: ChatIcon },
  { key: "dashboard", href: "/dashboard", available: false, Icon: DashboardIcon },
  { key: "settings", href: "/settings", available: true, Icon: SettingsIcon },
];

export function Sidebar() {
  const t = useTranslations("nav");
  const pathname = usePathname();

  return (
    <aside className="flex w-16 shrink-0 flex-col items-center gap-2 border-r border-slate-200 bg-white py-4 sm:w-60 sm:items-stretch sm:px-3 dark:border-slate-800 dark:bg-slate-950">
      <Link href="/chat" className="mb-4 flex items-center gap-3 px-1 sm:px-2">
        <Image src="/lokyy-logo.png" alt="Lokyy" width={32} height={32} priority />
        <span className="hidden text-lg font-extrabold tracking-tight sm:inline">
          lokyy<span className="grad-text"> workspace</span>
        </span>
      </Link>

      <nav className="flex flex-col gap-1">
        {NAV.map(({ key, href, Icon, available }) => {
          const active = pathname === href || pathname.startsWith(href + "/");
          const base =
            "flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition";
          if (!available) {
            return (
              <span
                key={key}
                aria-disabled="true"
                title={t("comingSoon")}
                className={`${base} cursor-not-allowed text-slate-400 dark:text-slate-600`}
              >
                <Icon />
                <span className="hidden sm:inline">{t(key)}</span>
                <span className="ml-auto hidden rounded bg-slate-100 px-1.5 py-0.5 text-[10px] text-slate-400 sm:inline dark:bg-slate-800">
                  {t("soon")}
                </span>
              </span>
            );
          }
          return (
            <Link
              key={key}
              href={href}
              aria-current={active ? "page" : undefined}
              className={`${base} ${
                active
                  ? "grad text-white shadow-sm"
                  : "text-slate-700 hover:bg-slate-100 dark:text-slate-300 dark:hover:bg-slate-800"
              }`}
            >
              <Icon />
              <span className="hidden sm:inline">{t(key)}</span>
            </Link>
          );
        })}
      </nav>
    </aside>
  );
}
