"use client";

// Auth state for the whole app (F1). Loads /auth/me once on mount so a page
// reload keeps the user logged in, and exposes login/signup/logout actions.
import { createContext, useCallback, useContext, useEffect, useState } from "react";

import {
  type AuthUser,
  type LoginInput,
  type SignupInput,
  fetchMe,
  login as apiLogin,
  logout as apiLogout,
  signup as apiSignup,
} from "@/lib/auth";

interface AuthContextValue {
  user: AuthUser | null;
  /** True until the initial /auth/me check resolves — avoids login flicker. */
  loading: boolean;
  login: (input: LoginInput) => Promise<AuthUser>;
  signup: (input: SignupInput) => Promise<AuthUser>;
  logout: () => Promise<void>;
  refresh: () => Promise<void>;
}

const AuthContext = createContext<AuthContextValue | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [loading, setLoading] = useState(true);

  const refresh = useCallback(async () => {
    try {
      setUser(await fetchMe());
    } catch {
      setUser(null);
    }
  }, []);

  useEffect(() => {
    let active = true;
    (async () => {
      try {
        const me = await fetchMe();
        if (active) setUser(me);
      } catch {
        if (active) setUser(null);
      } finally {
        if (active) setLoading(false);
      }
    })();
    return () => {
      active = false;
    };
  }, []);

  const login = useCallback(async (input: LoginInput) => {
    const u = await apiLogin(input);
    setUser(u);
    return u;
  }, []);

  const signup = useCallback(async (input: SignupInput) => {
    const u = await apiSignup(input);
    setUser(u);
    return u;
  }, []);

  const logout = useCallback(async () => {
    await apiLogout();
    setUser(null);
  }, []);

  return (
    <AuthContext.Provider value={{ user, loading, login, signup, logout, refresh }}>
      {children}
    </AuthContext.Provider>
  );
}

export function useAuth(): AuthContextValue {
  const ctx = useContext(AuthContext);
  if (!ctx) throw new Error("useAuth must be used within <AuthProvider>");
  return ctx;
}
