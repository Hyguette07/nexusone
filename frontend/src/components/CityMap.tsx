"use client";

import { DISTRICTS, projectKigali } from "@/lib/map";
import { TYPE_COLOR, TYPE_LABEL } from "@/lib/labels";
import { Incident, Resource } from "@/lib/types";
import Link from "next/link";

export function CityMap({
  incidents,
  resources = [],
}: {
  incidents: Incident[];
  resources?: Resource[];
}) {
  return (
    <div className="relative overflow-hidden rounded-2xl border border-white/10 bg-[#0d1014]">
      <svg viewBox="0 0 100 72" className="h-auto w-full text-white/20" aria-hidden>
        <rect width="100" height="72" fill="#0d1014" />
        <path d="M8 18 L28 12 L48 16 L70 10 L92 18 L88 40 L92 58 L70 64 L40 66 L12 58 Z" fill="#151a22" stroke="#2a3140" strokeWidth="0.4" />
        <path d="M22 20 C 28 28, 30 38, 26 50" fill="none" stroke="#38bdf8" strokeWidth="0.7" opacity="0.5" />
        <path d="M10 36 L90 30" fill="none" stroke="#ff5a1f" strokeWidth="0.35" opacity="0.5" />
        <path d="M18 12 L40 60" fill="none" stroke="#ff5a1f" strokeWidth="0.3" opacity="0.35" />
        <path d="M55 8 L60 66" fill="none" stroke="#2a3140" strokeWidth="0.4" />
      </svg>
      {DISTRICTS.map((d) => {
        const p = projectKigali(d.lat, d.lon);
        return (
          <span
            key={d.name}
            className="pointer-events-none absolute text-[9px] uppercase tracking-wider text-ash/80"
            style={{ left: `${p.x}%`, top: `${p.y}%` }}
          >
            {d.name}
          </span>
        );
      })}
      {resources.map((r) => {
        const p = projectKigali(r.latitude, r.longitude);
        return (
          <span
            key={`r-${r.id}`}
            title={`${r.name} (${r.resource_type})`}
            className="absolute h-2 w-2 -translate-x-1/2 -translate-y-1/2 rounded-sm bg-ok/80"
            style={{ left: `${p.x}%`, top: `${p.y}%` }}
          />
        );
      })}
      {incidents.map((inc) => {
        const p = projectKigali(inc.latitude, inc.longitude);
        const color = TYPE_COLOR[inc.incident_type];
        return (
          <Link
            key={inc.id}
            href={`/incidents/${inc.id}`}
            title={`${TYPE_LABEL[inc.incident_type]} — ${inc.title}`}
            className="absolute h-3.5 w-3.5 -translate-x-1/2 -translate-y-1/2 rounded-full shadow-[0_0_12px_currentColor]"
            style={{ left: `${p.x}%`, top: `${p.y}%`, background: color, color }}
          />
        );
      })}
      <p className="absolute bottom-2 left-3 text-[10px] uppercase tracking-[0.2em] text-ash">
        Kigali schematic · no map API key
      </p>
    </div>
  );
}
