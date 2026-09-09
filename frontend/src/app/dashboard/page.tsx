"use client";

import { AppShell, ErrorBanner, Skeleton } from "@/components/AppShell";
import { CityMap } from "@/components/CityMap";
import { api } from "@/lib/api";
import { TYPE_LABEL } from "@/lib/labels";
import { Dashboard } from "@/lib/types";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function DashboardPage() {
  const [data, setData] = useState<Dashboard | null>(null);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Dashboard>("/dashboard")
      .then(setData)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <p className="text-xs uppercase tracking-[0.3em] text-signal">Operations</p>
      <h1 className="mt-1 font-display text-5xl uppercase">City picture</h1>
      {loading ? <Skeleton className="mt-6 h-40" /> : null}
      {error ? <div className="mt-6"><ErrorBanner message={error} /></div> : null}
      {data ? (
        <>
          <div className="mt-8 grid gap-4 sm:grid-cols-3">
            <Stat title="Open" value={data.open_count} note="Waiting for a unit" />
            <Stat title="Assigned" value={data.assigned_count} note="En route or on scene" />
            <Stat title="Resolved" value={data.resolved_count} note="Closed in this demo" />
          </div>
          <div className="mt-4 grid gap-4 sm:grid-cols-3">
            <Stat title="Units available" value={data.available_resources} note={`${data.busy_resources} busy`} />
            <Stat title="Unread alerts" value={data.unread_notifications} note="In-app only" />
            <Stat
              title="Pub/sub"
              value={data.pubsub_mode}
              note={data.redis_connected ? "Redis connected" : "In-memory fallback"}
            />
          </div>
          <section className="mt-10 grid gap-8 lg:grid-cols-2">
            <div>
              <h2 className="font-display text-2xl uppercase">Recent incidents</h2>
              <ul className="mt-3 space-y-2">
                {data.recent_incidents.map((inc) => (
                  <li key={inc.id}>
                    <Link href={`/incidents/${inc.id}`} className="block rounded-xl border border-white/10 bg-panel px-4 py-3 hover:border-signal/50">
                      <p className="text-sm text-signal">{TYPE_LABEL[inc.incident_type]} · {inc.severity}</p>
                      <p className="font-medium">{inc.title}</p>
                      <p className="text-xs text-ash">{inc.location_name} · {inc.status}</p>
                    </Link>
                  </li>
                ))}
              </ul>
            </div>
            <div>
              <h2 className="font-display text-2xl uppercase">Live pins</h2>
              <div className="mt-3">
                <CityMap incidents={data.recent_incidents.filter((i) => i.status !== "RESOLVED" && i.status !== "CANCELLED")} />
              </div>
              <p className="mt-2 text-right text-sm">
                <Link className="text-signal underline" href="/board">Open the live board</Link>
              </p>
            </div>
          </section>
        </>
      ) : null}
    </AppShell>
  );
}

function Stat({ title, value, note }: { title: string; value: number | string; note: string }) {
  return (
    <div className="rounded-2xl border border-white/10 bg-panel p-5">
      <p className="text-xs uppercase tracking-[0.2em] text-ash">{title}</p>
      <p className="mt-2 font-display text-4xl uppercase text-signal">{value}</p>
      <p className="mt-1 text-xs text-ash">{note}</p>
    </div>
  );
}
