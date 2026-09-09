"use client";

import { DisclaimerBanner } from "@/components/Disclaimer";
import { useAuth } from "@/context/AuthContext";
import { Role } from "@/lib/types";
import Link from "next/link";
import { usePathname, useRouter } from "next/navigation";
import { useEffect } from "react";

const allLinks = [
  { href: "/dashboard", label: "Dashboard" },
  { href: "/board", label: "Live board" },
  { href: "/map", label: "Map" },
  { href: "/incidents", label: "Incidents" },
  { href: "/incidents/new", label: "Report" },
  { href: "/notifications", label: "Alerts" },
];

function linksFor(role: Role) {
  const extra =
    role === "CITIZEN"
      ? []
      : [{ href: "/resources", label: "Resources" }];
  return [...allLinks, ...extra];
}

export function AppShell({ children }: { children: React.ReactNode }) {
  const { user, ready, logout } = useAuth();
  const pathname = usePathname();
  const router = useRouter();

  useEffect(() => {
    if (ready && !user) router.replace("/login");
  }, [ready, user, router]);

  if (!ready) {
    return <div className="p-10 text-sm text-ash">Checking session…</div>;
  }
  if (!user) return null;

  const links = linksFor(user.role);

  return (
    <div className="min-h-screen lg:grid lg:grid-cols-[220px_1fr]">
      <aside className="border-b border-white/10 bg-panel lg:border-b-0 lg:border-r lg:border-white/10">
        <div className="px-5 py-6">
          <p className="font-display text-3xl uppercase tracking-tight text-paper">NexusOne</p>
          <p className="mt-1 text-[10px] uppercase tracking-[0.28em] text-signal">Dispatch desk</p>
        </div>
        <nav className="flex gap-1 overflow-x-auto px-3 pb-4 lg:flex-col">
          {links.map((link) => (
            <Link
              key={link.href}
              href={link.href}
              className={`whitespace-nowrap rounded-md px-3 py-2 text-sm ${
                pathname === link.href ? "bg-signal text-charcoal" : "text-ash hover:bg-white/5 hover:text-paper"
              }`}
            >
              {link.label}
            </Link>
          ))}
        </nav>
        <div className="hidden px-5 pb-6 text-xs text-ash lg:block">
          <p className="text-paper">{user.full_name}</p>
          <p className="mt-1 uppercase tracking-wider">{user.role}</p>
          <button className="mt-4 text-signal underline" onClick={() => { logout(); router.push("/login"); }}>
            Sign out
          </button>
        </div>
      </aside>
      <div>
        <header className="flex items-center justify-between border-b border-white/10 bg-panel px-4 py-3 lg:hidden">
          <p className="text-sm">
            {user.full_name} · {user.role}
          </p>
          <button className="text-sm text-signal underline" onClick={() => { logout(); router.push("/login"); }}>
            Sign out
          </button>
        </header>
        <main className="mx-auto max-w-6xl px-4 py-8">
          <div className="mb-6">
            <DisclaimerBanner compact />
          </div>
          {children}
        </main>
      </div>
    </div>
  );
}

export function EmptyState({ title, body }: { title: string; body: string }) {
  return (
    <div className="rounded-2xl border border-dashed border-white/15 bg-panel p-8 text-center">
      <p className="font-display text-2xl uppercase tracking-wide">{title}</p>
      <p className="mt-2 text-sm text-ash">{body}</p>
    </div>
  );
}

export function ErrorBanner({ message }: { message: string }) {
  return (
    <div className="rounded-xl border border-crit/40 bg-crit/10 px-4 py-3 text-sm text-crit" role="alert">
      {message}
    </div>
  );
}

export function Skeleton({ className = "h-24" }: { className?: string }) {
  return <div className={`animate-pulse rounded-2xl bg-white/10 ${className}`} />;
}
