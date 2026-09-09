from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, selectinload

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.assignment import Assignment
from app.models.enums import AssignmentStatus, IncidentStatus, ResourceStatus, Role
from app.models.incident import Incident
from app.models.resource import Resource
from app.models.user import User
from app.schemas.assignment import AssignmentCreate, AssignmentUpdate
from app.schemas.common import ok
from app.services.dispatch_ranker import DispatchRanker, RankableIncident, RankableResource
from app.services.notify import notify, notify_roles
from app.services.serializers import assignment_out, incident_payload

router = APIRouter(prefix="/assignments", tags=["assignments"])

ACTIVE = {AssignmentStatus.PENDING, AssignmentStatus.ACCEPTED, AssignmentStatus.EN_ROUTE, AssignmentStatus.ON_SCENE}


def _load(db: Session, assignment_id: int) -> Assignment:
    row = (
        db.query(Assignment)
        .options(selectinload(Assignment.incident), selectinload(Assignment.resource))
        .filter(Assignment.id == assignment_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Assignment not found")
    return row


@router.get("")
def list_assignments(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    incident_id: int | None = None,
    status_filter: AssignmentStatus | None = Query(default=None, alias="status"),
):
    q = db.query(Assignment).options(selectinload(Assignment.incident), selectinload(Assignment.resource))
    if incident_id:
        q = q.filter(Assignment.incident_id == incident_id)
    if status_filter:
        q = q.filter(Assignment.status == status_filter)
    if user.role == Role.RESPONDER:
        q = q.filter(Assignment.responder_id == user.id)
    elif user.role == Role.CITIZEN:
        q = q.join(Incident).filter(Incident.reporter_id == user.id)
    rows = q.order_by(Assignment.assigned_at.desc()).limit(200).all()
    return ok([assignment_out(r).model_dump(mode="json") for r in rows])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_assignment(
    body: AssignmentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    if user.role not in {Role.DISPATCHER, Role.ADMIN}:
        raise HTTPException(status_code=403, detail="Only dispatchers can assign resources")
    incident = db.get(Incident, body.incident_id)
    resource = db.get(Resource, body.resource_id)
    if incident is None or resource is None:
        raise HTTPException(status_code=404, detail="Incident or resource not found")
    if resource.status == ResourceStatus.OFFLINE:
        raise HTTPException(status_code=409, detail="Resource is offline")
    if incident.status in {IncidentStatus.RESOLVED, IncidentStatus.CANCELLED}:
        raise HTTPException(status_code=409, detail="Incident is closed")

    ranked = DispatchRanker().score_one(
        RankableIncident(
            incident_type=incident.incident_type.value,
            latitude=incident.latitude,
            longitude=incident.longitude,
            severity=incident.severity.value,
        ),
        RankableResource(
            id=resource.id,
            name=resource.name,
            resource_type=resource.resource_type.value,
            latitude=resource.latitude,
            longitude=resource.longitude,
            capacity=resource.capacity,
            current_load=resource.current_load,
            status=resource.status.value,
        ),
    )
    responder = db.query(User).filter(User.role == Role.RESPONDER, User.is_active.is_(True)).first()
    row = Assignment(
        incident_id=incident.id,
        resource_id=resource.id,
        assigned_by_id=user.id,
        responder_id=responder.id if responder else None,
        status=AssignmentStatus.PENDING,
        notes=body.notes,
        ranker_score=ranked.score,
        ranker_reason="; ".join(ranked.reasons),
    )
    db.add(row)
    incident.status = IncidentStatus.ASSIGNED
    resource.current_load = min(resource.capacity, resource.current_load + 1)
    if resource.current_load >= resource.capacity:
        resource.status = ResourceStatus.BUSY
    notify(db, incident.reporter_id, "Unit assigned", f"{resource.name} assigned to {incident.title} (simulation).", incident.id)
    if responder:
        notify(db, responder.id, "New assignment", f"Respond with {resource.name} to {incident.title} (simulation).", incident.id)
    notify_roles(db, [Role.DISPATCHER, Role.ADMIN], "Assignment created", f"{resource.name} → {incident.title}", incident.id)
    db.commit()
    db.refresh(row)
    row = _load(db, row.id)
    payload = assignment_out(row).model_dump(mode="json")
    if hasattr(request.app.state, "broker"):
        await request.app.state.broker.publish({"event": "assignment.created", "payload": payload})
        await request.app.state.broker.publish({"event": "incident.updated", "payload": incident_payload(incident)})
    return ok(payload, "Resource assigned. Simulation only.")


@router.get("/{assignment_id}")
def get_assignment(assignment_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    return ok(assignment_out(_load(db, assignment_id)).model_dump(mode="json"))


@router.patch("/{assignment_id}")
async def update_assignment(
    assignment_id: int,
    body: AssignmentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _load(db, assignment_id)
    if user.role == Role.CITIZEN:
        raise HTTPException(status_code=403, detail="Citizens cannot update assignments")
    if user.role == Role.RESPONDER and row.responder_id not in {None, user.id}:
        raise HTTPException(status_code=403, detail="Not your assignment")

    if body.status:
        row.status = body.status
        incident = row.incident
        resource = row.resource
        if body.status == AssignmentStatus.EN_ROUTE:
            incident.status = IncidentStatus.EN_ROUTE
        elif body.status == AssignmentStatus.ON_SCENE:
            incident.status = IncidentStatus.ON_SCENE
        elif body.status == AssignmentStatus.COMPLETED:
            incident.status = IncidentStatus.RESOLVED
            incident.resolved_at = datetime.now(timezone.utc)
            resource.current_load = max(0, resource.current_load - 1)
            if resource.current_load < resource.capacity and resource.status == ResourceStatus.BUSY:
                resource.status = ResourceStatus.AVAILABLE
        elif body.status == AssignmentStatus.DECLINED:
            resource.current_load = max(0, resource.current_load - 1)
            still = (
                db.query(Assignment)
                .filter(Assignment.incident_id == incident.id, Assignment.id != row.id, Assignment.status.in_(ACTIVE))
                .count()
            )
            if still == 0:
                incident.status = IncidentStatus.OPEN
        if user.role == Role.RESPONDER:
            row.responder_id = user.id
    if body.notes is not None:
        row.notes = body.notes
    db.commit()
    row = _load(db, assignment_id)
    payload = assignment_out(row).model_dump(mode="json")
    if hasattr(request.app.state, "broker"):
        await request.app.state.broker.publish({"event": "assignment.updated", "payload": payload})
        await request.app.state.broker.publish({"event": "incident.updated", "payload": incident_payload(row.incident)})
    return ok(payload)
