"use client";

import { AppShell } from "@/components/AppShell";
import { CityMap } from "@/components/CityMap";
import { useIncidentSocket } from "@/hooks/useIncidentSocket";
import { severityTone, statusTone, TYPE_LABEL } from "@/lib/labels";
import Link from "next/link";

export default function BoardPage() {
  const { incidents, mode, live, suggestions } = useIncidentSocket();

  return (
    <AppShell>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-signal">WebSocket</p>
          <h1 className="mt-1 font-display text-5xl uppercase">Live board</h1>
        </div>
        <p className="text-xs uppercase tracking-widest">
          <span className={live ? "text-ok" : "text-crit"}>{live ? "● live" : "○ reconnecting"}</span>
          <span className="ml-3 text-ash">pubsub {mode}</span>
        </p>
      </div>
      <div className="mt-6">
        <CityMap incidents={incidents} />
      </div>
      {suggestions.length > 0 ? (
        <section className="mt-8">
          <h2 className="font-display text-xl uppercase text-signal">DispatchRanker suggestions</h2>
          <ul className="mt-2 space-y-1 text-sm text-ash">
            {suggestions.map((s) => (
              <li key={s.incident_id}>
                Incident #{s.incident_id} → {s.resource_name}{" "}
                <span className="text-signal">score {s.score}</span>
              </li>
            ))}
          </ul>
        </section>
      ) : null}
      <ul className="mt-8 grid gap-3 md:grid-cols-2">
        {incidents.map((inc) => (
          <li key={inc.id}>
            <Link href={`/incidents/${inc.id}`} className="block rounded-2xl border border-white/10 bg-panel p-5 hover:border-signal/40">
              <div className="flex items-center justify-between gap-2">
                <span className="text-xs uppercase tracking-widest text-signal">{TYPE_LABEL[inc.incident_type]}</span>
                <span className={`rounded-full border px-2 py-0.5 text-[10px] uppercase ${statusTone(inc.status)}`}>{inc.status}</span>
              </div>
              <p className="mt-2 font-display text-2xl uppercase">{inc.title}</p>
              <p className="mt-1 text-sm text-ash">{inc.location_name}</p>
              <p className={`mt-2 text-xs uppercase ${severityTone(inc.severity)}`}>{inc.severity}</p>
            </Link>
          </li>
        ))}
      </ul>
      {incidents.length === 0 ? <p className="mt-8 text-ash">No live incidents. Report one from the form.</p> : null}
    </AppShell>
  );
}
