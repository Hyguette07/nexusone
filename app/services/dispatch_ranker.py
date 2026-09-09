"""DispatchRanker — scores which city resource should respond to an incident.

Pure scoring. No database, no I/O. Unit-test this module in isolation.

Score bands (max 100):
  type match     0–40
  distance       0–35   (0 km → 35, ≥15 km → 0)
  spare capacity 0–15
  availability   0–10   (AVAILABLE = 10, BUSY = 0 plus a −15 busy penalty)

OFFLINE units are returned as ineligible with score 0.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.services.geo import haversine_km

TYPE_AFFINITY: dict[str, dict[str, float]] = {
    "FIRE": {
        "FIRE_UNIT": 40,
        "AMBULANCE": 12,
        "VOLUNTEER_TEAM": 18,
        "BUS": 8,
        "SHELTER": 6,
        "CLINIC": 8,
    },
    "MEDICAL": {
        "AMBULANCE": 40,
        "CLINIC": 35,
        "VOLUNTEER_TEAM": 12,
        "FIRE_UNIT": 10,
        "SHELTER": 8,
        "BUS": 5,
    },
    "FLOOD": {
        "SHELTER": 38,
        "BUS": 32,
        "VOLUNTEER_TEAM": 28,
        "FIRE_UNIT": 16,
        "AMBULANCE": 10,
        "CLINIC": 8,
    },
    "MISSING_PERSON": {
        "VOLUNTEER_TEAM": 40,
        "BUS": 22,
        "FIRE_UNIT": 16,
        "SHELTER": 10,
        "AMBULANCE": 8,
        "CLINIC": 5,
    },
}

DISTANCE_FULL_KM = 15.0
BUSY_PENALTY = 15.0
MAX_SCORE = 100.0


@dataclass(frozen=True)
class RankableIncident:
    incident_type: str
    latitude: float
    longitude: float
    severity: str = "MEDIUM"


@dataclass(frozen=True)
class RankableResource:
    id: int
    name: str
    resource_type: str
    latitude: float
    longitude: float
    capacity: int
    current_load: int
    status: str


@dataclass(frozen=True)
class RankedResource:
    resource_id: int
    name: str
    resource_type: str
    score: float
    distance_km: float
    type_match: float
    capacity_score: float
    availability_score: float
    eligible: bool
    reasons: list[str] = field(default_factory=list)


class DispatchRanker:
    """Deterministic dispatcher recommendation engine."""

    def score_one(self, incident: RankableIncident, resource: RankableResource) -> RankedResource:
        distance = haversine_km(
            incident.latitude, incident.longitude, resource.latitude, resource.longitude
        )
        reasons: list[str] = []

        type_match = TYPE_AFFINITY.get(incident.incident_type, {}).get(resource.resource_type, 0.0)
        if type_match >= 35:
            reasons.append(f"strong type match ({resource.resource_type} ↔ {incident.incident_type})")
        elif type_match >= 20:
            reasons.append(f"usable type match ({resource.resource_type})")
        elif type_match > 0:
            reasons.append(f"weak type match ({resource.resource_type})")
        else:
            reasons.append(f"type mismatch ({resource.resource_type} vs {incident.incident_type})")

        dist_score = max(0.0, 35.0 * (1.0 - min(distance, DISTANCE_FULL_KM) / DISTANCE_FULL_KM))
        reasons.append(f"{distance:.1f} km from scene")

        capacity = max(resource.capacity, 1)
        spare_ratio = max(0, capacity - max(resource.current_load, 0)) / capacity
        capacity_score = spare_ratio * 15.0
        reasons.append(f"capacity {resource.current_load}/{resource.capacity}")

        status = resource.status.upper()
        eligible = status != "OFFLINE"
        if status == "AVAILABLE":
            availability = 10.0
            reasons.append("unit available")
            busy_penalty = 0.0
        elif status == "BUSY":
            availability = 0.0
            busy_penalty = BUSY_PENALTY
            reasons.append("already busy (−15)")
        else:
            availability = 0.0
            busy_penalty = 0.0
            reasons.append("offline — not eligible")

        severity_boost = 0.0
        if incident.severity == "CRITICAL" and dist_score >= 20:
            severity_boost = 4.0
            reasons.append("critical incident prefers nearby units")
        elif incident.severity == "HIGH" and dist_score >= 25:
            severity_boost = 2.0

        raw = type_match + dist_score + capacity_score + availability + severity_boost - busy_penalty
        score = max(0.0, min(MAX_SCORE, round(raw, 2)))
        if not eligible:
            score = 0.0

        return RankedResource(
            resource_id=resource.id,
            name=resource.name,
            resource_type=resource.resource_type,
            score=score,
            distance_km=round(distance, 3),
            type_match=type_match,
            capacity_score=round(capacity_score, 2),
            availability_score=availability,
            eligible=eligible,
            reasons=reasons,
        )

    def rank(
        self,
        incident: RankableIncident,
        resources: list[RankableResource],
        *,
        include_ineligible: bool = False,
        limit: int | None = None,
    ) -> list[RankedResource]:
        ranked = [self.score_one(incident, r) for r in resources]
        if not include_ineligible:
            ranked = [r for r in ranked if r.eligible]
        ranked.sort(key=lambda r: (-r.score, r.distance_km, r.name))
        if limit is not None:
            ranked = ranked[:limit]
        return ranked

    def best(self, incident: RankableIncident, resources: list[RankableResource]) -> RankedResource | None:
        ranked = self.rank(incident, resources, limit=1)
        return ranked[0] if ranked else None
