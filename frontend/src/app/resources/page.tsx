"use client";

import { AppShell, ErrorBanner, Skeleton } from "@/components/AppShell";
import { api } from "@/lib/api";
import { RESOURCE_LABEL } from "@/lib/labels";
import { Resource } from "@/lib/types";
import { useEffect, useState } from "react";

export default function ResourcesPage() {
  const [rows, setRows] = useState<Resource[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    api<Resource[]>("/resources")
      .then(setRows)
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <p className="text-xs uppercase tracking-[0.3em] text-signal">City assets</p>
      <h1 className="mt-1 font-display text-5xl uppercase">Resources</h1>
      {loading ? <Skeleton className="mt-6 h-40" /> : null}
      {error ? <div className="mt-6"><ErrorBanner message={error} /></div> : null}
      <ul className="mt-6 grid gap-3 md:grid-cols-2">
        {rows.map((r) => (
          <li key={r.id} className="rounded-2xl border border-white/10 bg-panel p-5">
            <p className="text-xs uppercase tracking-widest text-signal">{RESOURCE_LABEL[r.resource_type]}</p>
            <p className="mt-1 font-display text-2xl uppercase">{r.name}</p>
            <p className="text-sm text-ash">{r.location_name}</p>
            <p className="mt-2 text-xs uppercase text-ash">
              {r.status} · load {r.current_load}/{r.capacity}
            </p>
          </li>
        ))}
      </ul>
    </AppShell>
  );
}
