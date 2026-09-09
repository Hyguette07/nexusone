"use client";

import { AppShell, EmptyState, ErrorBanner, Skeleton } from "@/components/AppShell";
import { api } from "@/lib/api";
import { AppNotification } from "@/lib/types";
import { useEffect, useState } from "react";

export default function NotificationsPage() {
  const [rows, setRows] = useState<AppNotification[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<AppNotification[]>("/notifications")
      .then(setRows)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  async function markRead(id: number) {
    const updated = await api<AppNotification>(`/notifications/${id}/read`, { method: "PATCH" });
    setRows((prev) => prev.map((n) => (n.id === id ? updated : n)));
  }

  return (
    <AppShell>
      <p className="text-xs uppercase tracking-[0.3em] text-signal">Inbox</p>
      <h1 className="mt-1 font-display text-5xl uppercase">Alerts</h1>
      {loading ? <Skeleton className="mt-6 h-40" /> : null}
      {error ? <div className="mt-6"><ErrorBanner message={error} /></div> : null}
      {!loading && rows.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="Quiet" body="No simulation alerts yet." />
        </div>
      ) : (
        <ul className="mt-6 space-y-2">
          {rows.map((n) => (
            <li key={n.id} className={`rounded-xl border px-4 py-3 ${n.read ? "border-white/10 bg-panel" : "border-signal/40 bg-signal/5"}`}>
              <p className="font-medium">{n.title}</p>
              <p className="text-sm text-ash">{n.body}</p>
              {!n.read ? (
                <button className="mt-2 text-xs text-signal underline" onClick={() => markRead(n.id)}>
                  Mark read
                </button>
              ) : null}
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
