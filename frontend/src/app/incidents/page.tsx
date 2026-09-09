"use client";

import { AppShell, EmptyState, ErrorBanner, Skeleton } from "@/components/AppShell";
import { api } from "@/lib/api";
import { statusTone, TYPE_LABEL } from "@/lib/labels";
import { Incident, IncidentStatus, IncidentType } from "@/lib/types";
import Link from "next/link";
import { useEffect, useState } from "react";

export default function IncidentsPage() {
  const [rows, setRows] = useState<Incident[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);
  const [status, setStatus] = useState<IncidentStatus | "">("");
  const [type, setType] = useState<IncidentType | "">("");

  useEffect(() => {
    const q = new URLSearchParams();
    if (status) q.set("status", status);
    if (type) q.set("type", type);
    const suffix = q.toString() ? `?${q}` : "";
    setLoading(true);
    api<Incident[]>(`/incidents${suffix}`)
      .then(setRows)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, [status, type]);

  return (
    <AppShell>
      <div className="flex flex-wrap items-end justify-between gap-4">
        <div>
          <p className="text-xs uppercase tracking-[0.3em] text-signal">Queue</p>
          <h1 className="mt-1 font-display text-5xl uppercase">Incidents</h1>
        </div>
        <Link href="/incidents/new" className="rounded-md bg-signal px-4 py-2 text-sm text-charcoal">
          Report incident
        </Link>
      </div>
      <div className="mt-6 flex flex-wrap gap-3">
        <select className="rounded-md px-3 py-2 text-sm" value={status} onChange={(e) => setStatus(e.target.value as IncidentStatus | "")}>
          <option value="">All statuses</option>
          {["OPEN", "ASSIGNED", "EN_ROUTE", "ON_SCENE", "RESOLVED", "CANCELLED"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
        <select className="rounded-md px-3 py-2 text-sm" value={type} onChange={(e) => setType(e.target.value as IncidentType | "")}>
          <option value="">All types</option>
          {["FLOOD", "MEDICAL", "FIRE", "MISSING_PERSON"].map((s) => (
            <option key={s} value={s}>{s}</option>
          ))}
        </select>
      </div>
      {loading ? <Skeleton className="mt-6 h-40" /> : null}
      {error ? <div className="mt-6"><ErrorBanner message={error} /></div> : null}
      {!loading && rows.length === 0 ? (
        <div className="mt-6">
          <EmptyState title="No incidents" body="Change filters or file a simulation report." />
        </div>
      ) : (
        <ul className="mt-6 space-y-2">
          {rows.map((inc) => (
            <li key={inc.id}>
              <Link href={`/incidents/${inc.id}`} className="flex items-center justify-between rounded-xl border border-white/10 bg-panel px-4 py-3 hover:border-signal/40">
                <div>
                  <p className="text-xs uppercase tracking-widest text-signal">{TYPE_LABEL[inc.incident_type]}</p>
                  <p className="font-medium">{inc.title}</p>
                  <p className="text-xs text-ash">{inc.location_name}</p>
                </div>
                <span className={`rounded-full border px-2 py-0.5 text-[10px] uppercase ${statusTone(inc.status)}`}>{inc.status}</span>
              </Link>
            </li>
          ))}
        </ul>
      )}
    </AppShell>
  );
}
