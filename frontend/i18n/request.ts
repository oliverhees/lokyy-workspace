// i18n request config (next-intl, without URL routing).
// Locale comes from a cookie — German by default, English switchable.
// Multilanguage is base architecture: no hardcoded UI strings (see CLAUDE.md).
import { cookies } from "next/headers";
import { getRequestConfig } from "next-intl/server";

export const locales = ["de", "en"] as const;
export const defaultLocale = "de";

export default getRequestConfig(async () => {
  const store = await cookies();
  const cookieLocale = store.get("locale")?.value;
  const locale = locales.includes(cookieLocale as never) ? cookieLocale! : defaultLocale;
  return {
    locale,
    messages: (await import(`../messages/${locale}.json`)).default,
  };
});
