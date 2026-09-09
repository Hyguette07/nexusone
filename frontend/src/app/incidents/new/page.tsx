"use client";

import { AppShell, ErrorBanner } from "@/components/AppShell";
import { api } from "@/lib/api";
import { Incident, IncidentSeverity, IncidentType } from "@/lib/types";
import { useRouter } from "next/navigation";
import { FormEvent, useState } from "react";

const PLACES = [
  { name: "Nyabugogo bus park", lat: -1.9397, lon: 30.0444 },
  { name: "Nyamirambo", lat: -1.9801, lon: 30.0398 },
  { name: "Kimironko market", lat: -1.9494, lon: 30.1252 },
  { name: "Kacyiru", lat: -1.9442, lon: 30.0781 },
  { name: "Gikondo", lat: -1.9754, lon: 30.0752 },
];

export default function ReportPage() {
  const router = useRouter();
  const [title, setTitle] = useState("");
  const [description, setDescription] = useState("");
  const [incidentType, setIncidentType] = useState<IncidentType>("FLOOD");
  const [severity, setSeverity] = useState<IncidentSeverity>("MEDIUM");
  const [place, setPlace] = useState(0);
  const [error, setError] = useState("");
  const [pending, setPending] = useState(false);

  async function onSubmit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setPending(true);
    try {
      const loc = PLACES[place];
      const created = await api<Incident>("/incidents", {
        method: "POST",
        body: JSON.stringify({
          title,
          description,
          incident_type: incidentType,
          severity,
          latitude: loc.lat,
          longitude: loc.lon,
          location_name: loc.name,
        }),
      });
      router.push(`/incidents/${created.id}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : "Could not file report");
    } finally {
      setPending(false);
    }
  }

  return (
    <AppShell>
      <p className="text-xs uppercase tracking-[0.3em] text-signal">Citizen / any role</p>
      <h1 className="mt-1 font-display text-5xl uppercase">Report an incident</h1>
      <p className="mt-2 text-sm text-ash">Simulation only. Pick a Kigali landmark so the schematic map has a pin.</p>
      <form onSubmit={onSubmit} className="mt-8 max-w-xl space-y-4">
        <label className="block text-sm text-ash">
          Title
          <input className="mt-1 w-full rounded-md px-3 py-2" required minLength={3} value={title} onChange={(e) => setTitle(e.target.value)} />
        </label>
        <label className="block text-sm text-ash">
          What is happening
          <textarea className="mt-1 w-full rounded-md px-3 py-2" required minLength={8} rows={4} value={description} onChange={(e) => setDescription(e.target.value)} />
        </label>
        <div className="grid gap-4 sm:grid-cols-2">
          <label className="block text-sm text-ash">
            Type
            <select className="mt-1 w-full rounded-md px-3 py-2" value={incidentType} onChange={(e) => setIncidentType(e.target.value as IncidentType)}>
              <option value="FLOOD">Flood</option>
              <option value="MEDICAL">Medical</option>
              <option value="FIRE">Fire</option>
              <option value="MISSING_PERSON">Missing person</option>
            </select>
          </label>
          <label className="block text-sm text-ash">
            Severity
            <select className="mt-1 w-full rounded-md px-3 py-2" value={severity} onChange={(e) => setSeverity(e.target.value as IncidentSeverity)}>
              <option value="LOW">Low</option>
              <option value="MEDIUM">Medium</option>
              <option value="HIGH">High</option>
              <option value="CRITICAL">Critical</option>
            </select>
          </label>
        </div>
        <label className="block text-sm text-ash">
          Location
          <select className="mt-1 w-full rounded-md px-3 py-2" value={place} onChange={(e) => setPlace(Number(e.target.value))}>
            {PLACES.map((p, i) => (
              <option key={p.name} value={i}>{p.name}</option>
            ))}
          </select>
        </label>
        {error ? <ErrorBanner message={error} /> : null}
        <button disabled={pending} className="rounded-md bg-signal px-6 py-3 text-charcoal disabled:opacity-60">
          {pending ? "Sending…" : "File simulation report"}
        </button>
      </form>
    </AppShell>
  );
}
