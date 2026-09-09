"use client";

import { AppShell, ErrorBanner, Skeleton } from "@/components/AppShell";
import { useAuth } from "@/context/AuthContext";
import { api } from "@/lib/api";
import { RESOURCE_LABEL, scoreBand, severityTone, statusTone, TYPE_LABEL } from "@/lib/labels";
import { Assignment, AssignmentStatus, Incident, RankedResource, ResourceType } from "@/lib/types";
import { useParams } from "next/navigation";
import { useCallback, useEffect, useState } from "react";

export default function IncidentDetailPage() {
  const params = useParams<{ id: string }>();
  const id = Number(params.id);
  const { user } = useAuth();
  const canDispatch = user?.role === "DISPATCHER" || user?.role === "ADMIN";
  const canRespond = user?.role === "RESPONDER" || canDispatch;

  const [incident, setIncident] = useState<Incident | null>(null);
  const [ranked, setRanked] = useState<RankedResource[]>([]);
  const [assignments, setAssignments] = useState<Assignment[]>([]);
  const [error, setError] = useState("");
  const [busy, setBusy] = useState("");

  const load = useCallback(async () => {
    const inc = await api<Incident>(`/incidents/${id}`);
    setIncident(inc);
    const asg = await api<Assignment[]>(`/assignments?incident_id=${id}`);
    setAssignments(asg);
    if (canDispatch || user?.role === "RESPONDER") {
      const ranks = await api<RankedResource[]>(`/incidents/${id}/rankings`);
      setRanked(ranks);
    }
  }, [id, canDispatch, user?.role]);

  useEffect(() => {
    load().catch((e: Error) => setError(e.message));
  }, [load]);

  async function assign(resourceId: number) {
    setBusy("assign");
    setError("");
    try {
      await api("/assignments", {
        method: "POST",
        body: JSON.stringify({ incident_id: id, resource_id: resourceId }),
      });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Assign failed");
    } finally {
      setBusy("");
    }
  }

  async function patchAssignment(assignmentId: number, status: AssignmentStatus) {
    setBusy(`asg-${assignmentId}`);
    setError("");
    try {
      await api(`/assignments/${assignmentId}`, {
        method: "PATCH",
        body: JSON.stringify({ status }),
      });
      await load();
    } catch (e) {
      setError(e instanceof Error ? e.message : "Update failed");
    } finally {
      setBusy("");
    }
  }

  if (!incident) {
    return (
      <AppShell>
        {error ? <ErrorBanner message={error} /> : <Skeleton className="h-48" />}
      </AppShell>
    );
  }

  return (
    <AppShell>
      <p className="text-xs uppercase tracking-[0.3em] text-signal">{TYPE_LABEL[incident.incident_type]}</p>
      <h1 className="mt-1 font-display text-5xl uppercase">{incident.title}</h1>
      <div className="mt-3 flex flex-wrap gap-2 text-xs uppercase">
        <span className={`rounded-full border px-2 py-0.5 ${statusTone(incident.status)}`}>{incident.status}</span>
        <span className={severityTone(incident.severity)}>{incident.severity}</span>
        <span className="text-ash">{incident.location_name}</span>
      </div>
      <p className="mt-4 max-w-2xl text-sm text-ash">{incident.description}</p>
      {error ? <div className="mt-4"><ErrorBanner message={error} /></div> : null}

      <section className="mt-10">
        <h2 className="font-display text-2xl uppercase">Assignments</h2>
        {assignments.length === 0 ? <p className="mt-2 text-sm text-ash">None yet.</p> : (
          <ul className="mt-3 space-y-2">
            {assignments.map((a) => (
              <li key={a.id} className="rounded-xl border border-white/10 bg-panel px-4 py-3">
                <p className="font-medium">{a.resource_name}</p>
                <p className="text-xs text-ash">
                  {a.status}
                  {a.ranker_score != null ? ` · DispatchRanker ${a.ranker_score}` : ""}
                </p>
                {a.ranker_reason ? <p className="mt-1 text-xs text-ash">{a.ranker_reason}</p> : null}
                {canRespond ? (
                  <div className="mt-2 flex flex-wrap gap-2">
                    {(["ACCEPTED", "EN_ROUTE", "ON_SCENE", "COMPLETED", "DECLINED"] as AssignmentStatus[]).map((s) => (
                      <button
                        key={s}
                        disabled={busy === `asg-${a.id}`}
                        className="rounded border border-white/15 px-2 py-1 text-[10px] uppercase hover:border-signal"
                        onClick={() => patchAssignment(a.id, s)}
                      >
                        {s}
                      </button>
                    ))}
                  </div>
                ) : null}
              </li>
            ))}
          </ul>
        )}
      </section>

      {ranked.length > 0 ? (
        <section className="mt-10">
          <h2 className="font-display text-2xl uppercase">DispatchRanker</h2>
          <p className="mt-1 text-sm text-ash">Distance, type match, spare capacity, already-busy.</p>
          <ul className="mt-4 space-y-2">
            {ranked.map((r) => (
              <li key={r.resource_id} className="flex flex-wrap items-center justify-between gap-3 rounded-xl border border-white/10 bg-panel px-4 py-3">
                <div>
                  <p className="font-medium">{r.name}</p>
                  <p className="text-xs text-ash">
                    {RESOURCE_LABEL[r.resource_type as ResourceType] ?? r.resource_type} · {r.distance_km.toFixed(1)} km ·{" "}
                    <span className="text-signal">score {r.score}</span> · {scoreBand(r.score)}
                  </p>
                  <p className="mt-1 text-[11px] text-ash">{r.reasons.join(" · ")}</p>
                </div>
                {canDispatch ? (
                  <button
                    disabled={busy === "assign" || !r.eligible}
                    onClick={() => assign(r.resource_id)}
                    className="rounded-md bg-signal px-3 py-2 text-xs text-charcoal disabled:opacity-40"
                  >
                    Assign
                  </button>
                ) : null}
              </li>
            ))}
          </ul>
        </section>
      ) : null}
    </AppShell>
  );
}
