"""Background loop: suggest DispatchRanker picks for unassigned OPEN incidents."""

from __future__ import annotations

import asyncio
import logging
from typing import Any

from sqlalchemy.orm import Session

from app.models.enums import IncidentStatus, ResourceStatus
from app.models.incident import Incident
from app.models.resource import Resource
from app.services.dispatch_ranker import DispatchRanker, RankableIncident, RankableResource

logger = logging.getLogger("nexusone.worker")


def _rankable_resources(rows: list[Resource]) -> list[RankableResource]:
    return [
        RankableResource(
            id=r.id,
            name=r.name,
            resource_type=r.resource_type.value,
            latitude=r.latitude,
            longitude=r.longitude,
            capacity=r.capacity,
            current_load=r.current_load,
            status=r.status.value,
        )
        for r in rows
        if r.status != ResourceStatus.OFFLINE
    ]


def build_suggestions(db: Session) -> list[dict[str, Any]]:
    ranker = DispatchRanker()
    open_incidents = (
        db.query(Incident)
        .filter(Incident.status == IncidentStatus.OPEN)
        .order_by(Incident.created_at.desc())
        .all()
    )
    resources = db.query(Resource).all()
    ranked_pool = _rankable_resources(resources)
    suggestions: list[dict[str, Any]] = []
    for incident in open_incidents:
        assigned_ids = {a.resource_id for a in incident.assignments if a.status.value not in {"COMPLETED", "DECLINED"}}
        if assigned_ids:
            continue
        best = ranker.best(
            RankableIncident(
                incident_type=incident.incident_type.value,
                latitude=incident.latitude,
                longitude=incident.longitude,
                severity=incident.severity.value,
            ),
            ranked_pool,
        )
        if best is None:
            continue
        suggestions.append(
            {
                "incident_id": incident.id,
                "incident_title": incident.title,
                "resource_id": best.resource_id,
                "resource_name": best.name,
                "score": best.score,
                "distance_km": best.distance_km,
                "reasons": best.reasons,
            }
        )
    return suggestions


async def run_worker(app_state: Any, interval: int) -> None:
    from app.database import SessionLocal

    while True:
        try:
            db = SessionLocal()
            try:
                suggestions = build_suggestions(db)
            finally:
                db.close()
            if suggestions and getattr(app_state, "broker", None):
                await app_state.broker.publish(
                    {
                        "event": "dispatch.suggestion",
                        "payload": {"suggestions": suggestions},
                    }
                )
        except asyncio.CancelledError:
            raise
        except Exception:
            logger.exception("Worker cycle failed")
        await asyncio.sleep(interval)
