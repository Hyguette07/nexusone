"use client";

import { AuthUser, Role } from "@/lib/types";
import { api, setToken, USER_KEY } from "@/lib/api";
import { createContext, useContext, useEffect, useMemo, useState } from "react";

type AuthState = {
  user: AuthUser | null;
  ready: boolean;
  login: (email: string, password: string) => Promise<AuthUser>;
  register: (payload: { email: string; password: string; full_name: string; phone?: string }) => Promise<AuthUser>;
  logout: () => void;
};

const Ctx = createContext<AuthState | null>(null);

export function AuthProvider({ children }: { children: React.ReactNode }) {
  const [user, setUser] = useState<AuthUser | null>(null);
  const [ready, setReady] = useState(false);

  useEffect(() => {
    const stored = typeof window !== "undefined" ? localStorage.getItem(USER_KEY) : null;
    if (stored) {
      try {
        setUser(JSON.parse(stored) as AuthUser);
      } catch {
        localStorage.removeItem(USER_KEY);
      }
    }
    setReady(true);
  }, []);

  const value = useMemo<AuthState>(
    () => ({
      user,
      ready,
      async login(email, password) {
        const data = await api<AuthUser>("/auth/login", {
          method: "POST",
          body: JSON.stringify({ email, password }),
        });
        setToken(data.token);
        localStorage.setItem(USER_KEY, JSON.stringify(data));
        setUser(data);
        return data;
      },
      async register(payload) {
        const data = await api<AuthUser>("/auth/register", {
          method: "POST",
          body: JSON.stringify(payload),
        });
        setToken(data.token);
        localStorage.setItem(USER_KEY, JSON.stringify(data));
        setUser(data);
        return data;
      },
      logout() {
        setToken(null);
        localStorage.removeItem(USER_KEY);
        setUser(null);
      },
    }),
    [user, ready]
  );

  return <Ctx.Provider value={value}>{children}</Ctx.Provider>;
}

export function useAuth() {
  const ctx = useContext(Ctx);
  if (!ctx) throw new Error("useAuth must be used inside AuthProvider");
  return ctx;
}

export function homeFor(role: Role) {
  if (role === "DISPATCHER" || role === "RESPONDER") return "/board";
  return "/dashboard";
}
