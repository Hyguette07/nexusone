import { IncidentSeverity, IncidentStatus, IncidentType, ResourceType } from "./types";

export const DISCLAIMER =
  "Educational simulation — not a 911 replacement. In a real emergency, call official services.";

export const TYPE_LABEL: Record<IncidentType, string> = {
  FLOOD: "Flood",
  MEDICAL: "Medical",
  FIRE: "Fire",
  MISSING_PERSON: "Missing person",
};

export const TYPE_COLOR: Record<IncidentType, string> = {
  FLOOD: "#38bdf8",
  MEDICAL: "#fb7185",
  FIRE: "#ff5a1f",
  MISSING_PERSON: "#f5c542",
};

export const RESOURCE_LABEL: Record<ResourceType, string> = {
  CLINIC: "Clinic",
  BUS: "City bus",
  SHELTER: "Shelter",
  VOLUNTEER_TEAM: "Volunteers",
  FIRE_UNIT: "Fire unit",
  AMBULANCE: "Ambulance",
};

export function severityTone(severity: IncidentSeverity) {
  if (severity === "CRITICAL") return "text-crit";
  if (severity === "HIGH") return "text-signal";
  if (severity === "MEDIUM") return "text-warn";
  return "text-ash";
}

export function statusTone(status: IncidentStatus) {
  if (status === "OPEN") return "border-signal text-signal";
  if (status === "RESOLVED") return "border-ok text-ok";
  if (status === "CANCELLED") return "border-ash text-ash";
  return "border-warn text-warn";
}

export function scoreBand(score: number) {
  if (score >= 80) return "Prime pick";
  if (score >= 60) return "Strong";
  if (score >= 40) return "Usable";
  return "Last resort";
}
