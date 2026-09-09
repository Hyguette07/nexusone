"use client";

import { getToken } from "@/lib/api";
import { Incident } from "@/lib/types";
import { useEffect, useRef, useState } from "react";

const WS = process.env.NEXT_PUBLIC_WS_URL ?? "ws://localhost:8085/ws/incidents";

type Frame = {
  event: string;
  payload?: {
    incidents?: Incident[];
    id?: number;
    suggestions?: { incident_id: number; resource_name: string; score: number }[];
    pubsub_mode?: string;
  };
};

export function useIncidentSocket() {
  const [incidents, setIncidents] = useState<Incident[]>([]);
  const [mode, setMode] = useState("connecting");
  const [suggestions, setSuggestions] = useState<{ incident_id: number; resource_name: string; score: number }[]>([]);
  const [live, setLive] = useState(false);
  const retry = useRef(0);

  useEffect(() => {
    let ws: WebSocket | null = null;
    let stopped = false;

    function connect() {
      const token = getToken();
      if (!token || stopped) return;
      ws = new WebSocket(`${WS}?token=${encodeURIComponent(token)}`);
      ws.onopen = () => {
        retry.current = 0;
        setLive(true);
      };
      ws.onmessage = (ev) => {
        const frame = JSON.parse(ev.data) as Frame;
        if (frame.event === "board.snapshot") {
          setIncidents(frame.payload?.incidents ?? []);
          if (frame.payload?.pubsub_mode) setMode(frame.payload.pubsub_mode);
        } else if (frame.event === "incident.created" || frame.event === "incident.updated") {
          const row = frame.payload as Incident;
          setIncidents((prev) => {
            const next = prev.filter((i) => i.id !== row.id);
            if (["RESOLVED", "CANCELLED"].includes(row.status)) return next;
            return [row, ...next];
          });
        } else if (frame.event === "incident.resolved") {
          const row = frame.payload as Incident;
          setIncidents((prev) => prev.filter((i) => i.id !== row.id));
        } else if (frame.event === "dispatch.suggestion") {
          setSuggestions(frame.payload?.suggestions ?? []);
        }
      };
      ws.onclose = () => {
        setLive(false);
        if (stopped) return;
        retry.current += 1;
        const wait = Math.min(8000, 600 * retry.current);
        setTimeout(connect, wait);
      };
    }

    connect();
    return () => {
      stopped = true;
      ws?.close();
    };
  }, []);

  return { incidents, mode, live, suggestions };
}
