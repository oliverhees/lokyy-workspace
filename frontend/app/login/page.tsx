"use client";

// F1 — Auth entry: login OR first-run signup (org + admin), with 2FA step.
import Image from "next/image";
import { useRouter } from "next/navigation";
import { useEffect, useState } from "react";
import { useTranslations } from "next-intl";

import { useAuth } from "@/components/auth/AuthProvider";
import { ConnectionSwitch } from "@/components/ConnectionSwitch";
import { LanguageSwitch } from "@/components/LanguageSwitch";
import { AuthApiError } from "@/lib/auth";

type Mode = "login" | "signup";

export default function LoginPage() {
  const t = useTranslations("auth");
  const router = useRouter();
  const { user, loading, login, signup } = useAuth();

  const [mode, setMode] = useState<Mode>("login");
  const [organizationName, setOrganizationName] = useState("");
  const [displayName, setDisplayName] = useState("");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [totp, setTotp] = useState("");
  const [needsTotp, setNeedsTotp] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [busy, setBusy] = useState(false);

  // Already authenticated → leave the login screen.
  useEffect(() => {
    if (!loading && user) router.replace("/chat");
  }, [loading, user, router]);

  async function onSubmit(e: React.FormEvent) {
    e.preventDefault();
    setError(null);
    setBusy(true);
    try {
      if (mode === "signup") {
        await signup({ organization_name: organizationName, email, password, display_name: displayName });
      } else {
        await login({ email, password, totp_code: needsTotp ? totp : undefined });
      }
      router.replace("/chat");
    } catch (err) {
      if (err instanceof AuthApiError) {
        // 401 on login with a 2FA-enabled account → reveal the code field.
        if (mode === "login" && err.status === 401 && /2fa/i.test(err.message)) {
          setNeedsTotp(true);
          setError(t("totpRequired"));
        } else {
          setError(mode === "signup" ? t("signupFailed") : t("loginFailed"));
        }
      } else {
        setError(t("networkError"));
      }
    } finally {
      setBusy(false);
    }
  }

  const inputClass =
    "w-full rounded-lg border border-slate-300 bg-white px-3 py-2 text-sm outline-none focus:border-brand-blue focus:ring-2 focus:ring-brand-blue/30 dark:border-slate-700 dark:bg-slate-900";

  return (
    <main className="flex min-h-screen flex-col">
      <header className="flex h-14 shrink-0 items-center justify-end gap-2 px-4">
        <ConnectionSwitch />
        <LanguageSwitch />
      </header>

      <div className="flex flex-1 items-center justify-center px-4 pb-16">
        <div className="w-full max-w-sm">
          <div className="mb-8 flex flex-col items-center text-center">
            <Image src="/lokyy-logo.png" alt="Lokyy" width={56} height={56} priority />
            <h1 className="mt-4 text-2xl font-extrabold tracking-tight">
              lokyy<span className="grad-text"> workspace</span>
            </h1>
            <p className="mt-1 text-sm text-slate-500 dark:text-slate-400">
              {mode === "signup" ? t("signupSubtitle") : t("loginSubtitle")}
            </p>
          </div>

          <form onSubmit={onSubmit} className="space-y-3" noValidate>
            {mode === "signup" && (
              <>
                <input
                  className={inputClass}
                  placeholder={t("organizationName")}
                  value={organizationName}
                  onChange={(e) => setOrganizationName(e.target.value)}
                  required
                  autoComplete="organization"
                />
                <input
                  className={inputClass}
                  placeholder={t("displayName")}
                  value={displayName}
                  onChange={(e) => setDisplayName(e.target.value)}
                  required
                  autoComplete="name"
                />
              </>
            )}
            <input
              className={inputClass}
              type="email"
              placeholder={t("email")}
              value={email}
              onChange={(e) => setEmail(e.target.value)}
              required
              autoComplete="email"
            />
            <input
              className={inputClass}
              type="password"
              placeholder={t("password")}
              value={password}
              onChange={(e) => setPassword(e.target.value)}
              required
              minLength={8}
              autoComplete={mode === "signup" ? "new-password" : "current-password"}
            />
            {mode === "login" && needsTotp && (
              <input
                className={inputClass}
                inputMode="numeric"
                placeholder={t("totpCode")}
                value={totp}
                onChange={(e) => setTotp(e.target.value)}
                autoComplete="one-time-code"
              />
            )}

            {error && (
              <p className="text-sm text-red-600 dark:text-red-400" role="alert">
                {error}
              </p>
            )}

            <button
              type="submit"
              disabled={busy}
              className="grad w-full rounded-lg px-4 py-2.5 text-sm font-semibold text-white shadow-sm transition hover:opacity-90 disabled:opacity-50"
            >
              {busy ? t("pleaseWait") : mode === "signup" ? t("signupCta") : t("loginCta")}
            </button>
          </form>

          <p className="mt-6 text-center text-sm text-slate-500 dark:text-slate-400">
            {mode === "signup" ? t("haveAccount") : t("noAccount")}{" "}
            <button
              type="button"
              onClick={() => {
                setMode(mode === "signup" ? "login" : "signup");
                setError(null);
                setNeedsTotp(false);
              }}
              className="font-semibold text-brand-blue hover:underline"
            >
              {mode === "signup" ? t("loginCta") : t("signupCta")}
            </button>
          </p>
        </div>
      </div>
    </main>
  );
}
