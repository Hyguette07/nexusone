from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, Query, Request, status
from sqlalchemy.orm import Session, selectinload

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.enums import IncidentSeverity, IncidentStatus, IncidentType, Role
from app.models.incident import Incident
from app.models.resource import Resource
from app.models.user import User
from app.schemas.common import ok
from app.schemas.incident import IncidentCreate, IncidentUpdate, RankedResourceOut
from app.services.dispatch_ranker import DispatchRanker, RankableIncident, RankableResource
from app.services.notify import notify, notify_roles
from app.services.serializers import incident_out, incident_payload

router = APIRouter(prefix="/incidents", tags=["incidents"])


def _load(db: Session, incident_id: int) -> Incident:
    row = (
        db.query(Incident)
        .options(selectinload(Incident.reporter), selectinload(Incident.assignments))
        .filter(Incident.id == incident_id)
        .first()
    )
    if row is None:
        raise HTTPException(status_code=404, detail="Incident not found")
    return row


@router.get("")
def list_incidents(
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    status_filter: IncidentStatus | None = Query(default=None, alias="status"),
    incident_type: IncidentType | None = Query(default=None, alias="type"),
    severity: IncidentSeverity | None = Query(default=None),
):
    q = db.query(Incident).options(selectinload(Incident.reporter), selectinload(Incident.assignments))
    if status_filter:
        q = q.filter(Incident.status == status_filter)
    if incident_type:
        q = q.filter(Incident.incident_type == incident_type)
    if severity:
        q = q.filter(Incident.severity == severity)
    if user.role == Role.CITIZEN:
        q = q.filter(
            (Incident.reporter_id == user.id)
            | (Incident.status.in_([IncidentStatus.OPEN, IncidentStatus.ASSIGNED, IncidentStatus.EN_ROUTE, IncidentStatus.ON_SCENE]))
        )
    rows = q.order_by(Incident.created_at.desc()).limit(200).all()
    return ok([incident_out(r).model_dump(mode="json") for r in rows])


@router.post("", status_code=status.HTTP_201_CREATED)
async def create_incident(
    body: IncidentCreate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = Incident(
        title=body.title,
        description=body.description,
        incident_type=body.incident_type,
        severity=body.severity,
        latitude=body.latitude,
        longitude=body.longitude,
        location_name=body.location_name,
        reporter_id=user.id,
        status=IncidentStatus.OPEN,
    )
    db.add(row)
    db.flush()
    notify(db, user.id, "Incident reported", f"{body.title} is on the live board (simulation).", row.id)
    notify_roles(
        db,
        [Role.DISPATCHER, Role.ADMIN],
        f"New {body.incident_type.value} — {body.severity.value}",
        f"{body.title} at {body.location_name}. Simulation — not a real dispatch.",
        row.id,
    )
    db.commit()
    db.refresh(row)
    row = _load(db, row.id)
    payload = incident_payload(row)
    if hasattr(request.app.state, "broker"):
        await request.app.state.broker.publish({"event": "incident.created", "payload": payload})
    return ok(payload, "Incident recorded. This is an educational simulation.")


@router.get("/{incident_id}")
def get_incident(incident_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    row = _load(db, incident_id)
    return ok(incident_out(row).model_dump(mode="json"))


@router.patch("/{incident_id}")
async def update_incident(
    incident_id: int,
    body: IncidentUpdate,
    request: Request,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
):
    row = _load(db, incident_id)
    if user.role == Role.CITIZEN:
        if row.reporter_id != user.id:
            raise HTTPException(status_code=403, detail="You can only update your own reports")
        if body.status and body.status not in {IncidentStatus.CANCELLED}:
            raise HTTPException(status_code=403, detail="Citizens may only cancel their reports")
    elif user.role == Role.RESPONDER:
        raise HTTPException(status_code=403, detail="Responders update assignments, not incidents")

    data = body.model_dump(exclude_unset=True)
    for key, value in data.items():
        setattr(row, key, value)
    if body.status in {IncidentStatus.RESOLVED, IncidentStatus.CANCELLED}:
        row.resolved_at = datetime.now(timezone.utc)
    db.commit()
    row = _load(db, incident_id)
    payload = incident_payload(row)
    if hasattr(request.app.state, "broker"):
        event = "incident.resolved" if row.status in {IncidentStatus.RESOLVED, IncidentStatus.CANCELLED} else "incident.updated"
        await request.app.state.broker.publish({"event": event, "payload": payload})
    return ok(payload)


@router.get("/{incident_id}/rankings")
def rank_resources(
    incident_id: int,
    db: Session = Depends(get_db),
    user: User = Depends(get_current_user),
    include_ineligible: bool = False,
    limit: int = Query(default=8, ge=1, le=50),
):
    if user.role not in {Role.DISPATCHER, Role.ADMIN, Role.RESPONDER}:
        raise HTTPException(status_code=403, detail="Ranking is for dispatch staff")
    incident = _load(db, incident_id)
    resources = db.query(Resource).all()
    ranker = DispatchRanker()
    ranked = ranker.rank(
        RankableIncident(
            incident_type=incident.incident_type.value,
            latitude=incident.latitude,
            longitude=incident.longitude,
            severity=incident.severity.value,
        ),
        [
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
            for r in resources
        ],
        include_ineligible=include_ineligible,
        limit=limit,
    )
    return ok([RankedResourceOut(**r.__dict__).model_dump() for r in ranked])
