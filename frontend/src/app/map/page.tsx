"use client";

import { AppShell, ErrorBanner, Skeleton } from "@/components/AppShell";
import { CityMap } from "@/components/CityMap";
import { api } from "@/lib/api";
import { Incident, Resource } from "@/lib/types";
import { useEffect, useState } from "react";

export default function MapPage() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [resources, setResources] = useState<Resource[]>([]);
  const [error, setError] = useState("");
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    Promise.all([api<Incident[]>("/incidents"), api<Resource[]>("/resources")])
      .then(([i, r]) => {
        setIncidents(i.filter((x) => x.status !== "RESOLVED" && x.status !== "CANCELLED"));
        setResources(r);
      })
      .catch((e: Error) => setError(e.message))
      .finally(() => setLoading(false));
  }, []);

  return (
    <AppShell>
      <p className="text-xs uppercase tracking-[0.3em] text-signal">Kigali</p>
      <h1 className="mt-1 font-display text-5xl uppercase">Pins on a schematic</h1>
      <p className="mt-2 max-w-xl text-sm text-ash">
        Orange / colour dots are open incidents. Green squares are resources. Coordinates around −1.95, 30.06.
        No Google Maps key required.
      </p>
      {loading ? <Skeleton className="mt-6 h-72" /> : null}
      {error ? <div className="mt-6"><ErrorBanner message={error} /></div> : null}
      <div className="mt-6">
        <CityMap incidents={incidents} resources={resources} />
      </div>
    </AppShell>
  );
}
