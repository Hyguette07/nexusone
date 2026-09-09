from app.models.assignment import Assignment
from app.models.enums import AssignmentStatus
from app.models.incident import Incident
from app.schemas.assignment import AssignmentOut
from app.schemas.incident import IncidentOut


def incident_out(row: Incident) -> IncidentOut:
    open_count = sum(
        1
        for a in (row.assignments or [])
        if a.status not in {AssignmentStatus.COMPLETED, AssignmentStatus.DECLINED}
    )
    return IncidentOut(
        id=row.id,
        title=row.title,
        description=row.description,
        incident_type=row.incident_type,
        status=row.status,
        severity=row.severity,
        latitude=row.latitude,
        longitude=row.longitude,
        location_name=row.location_name,
        reporter_id=row.reporter_id,
        reporter_name=row.reporter.full_name if row.reporter else None,
        created_at=row.created_at,
        updated_at=row.updated_at,
        resolved_at=row.resolved_at,
        open_assignment_count=open_count,
    )


def assignment_out(row: Assignment) -> AssignmentOut:
    return AssignmentOut(
        id=row.id,
        incident_id=row.incident_id,
        resource_id=row.resource_id,
        assigned_by_id=row.assigned_by_id,
        responder_id=row.responder_id,
        status=row.status,
        notes=row.notes,
        ranker_score=row.ranker_score,
        ranker_reason=row.ranker_reason,
        assigned_at=row.assigned_at,
        updated_at=row.updated_at,
        incident_title=row.incident.title if row.incident else None,
        resource_name=row.resource.name if row.resource else None,
    )


def incident_payload(row: Incident) -> dict:
    return incident_out(row).model_dump(mode="json")
