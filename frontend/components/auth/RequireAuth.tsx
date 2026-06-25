"use client";

// Route guard (F1): renders children only for an authenticated user.
// While /auth/me is in flight it shows a light placeholder; if there is no
// session it redirects to /login. Wrap any protected page with this.
import { useRouter } from "next/navigation";
import { useEffect } from "react";

import { useAuth } from "./AuthProvider";

export function RequireAuth({ children }: { children: React.ReactNode }) {
  const { user, loading } = useAuth();
  const router = useRouter();

  useEffect(() => {
    if (!loading && !user) router.replace("/login");
  }, [loading, user, router]);

  if (loading || !user) {
    return (
      <div className="flex min-h-screen items-center justify-center text-sm text-slate-400">
        …
      </div>
    );
  }
  return <>{children}</>;
}
