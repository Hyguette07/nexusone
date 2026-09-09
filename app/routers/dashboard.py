from fastapi import APIRouter, Depends, Request
from sqlalchemy.orm import Session, selectinload

from app.auth.deps import get_current_user
from app.database import get_db
from app.models.enums import IncidentStatus, ResourceStatus
from app.models.incident import Incident
from app.models.notification import Notification
from app.models.resource import Resource
from app.models.user import User
from app.schemas.common import ok
from app.services.serializers import incident_out

router = APIRouter(tags=["dashboard"])

OPENISH = {IncidentStatus.OPEN, IncidentStatus.ASSIGNED, IncidentStatus.EN_ROUTE, IncidentStatus.ON_SCENE}
ASSIGNEDISH = {IncidentStatus.ASSIGNED, IncidentStatus.EN_ROUTE, IncidentStatus.ON_SCENE}


@router.get("/dashboard")
def dashboard(request: Request, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    incidents = (
        db.query(Incident).options(selectinload(Incident.reporter), selectinload(Incident.assignments)).all()
    )
    resources = db.query(Resource).all()
    unread = (
        db.query(Notification)
        .filter(Notification.user_id == user.id, Notification.read.is_(False))
        .count()
    )
    broker = getattr(request.app.state, "broker", None)
    recent = sorted(incidents, key=lambda i: i.created_at, reverse=True)[:8]
    return ok(
        {
            "open_count": sum(1 for i in incidents if i.status in OPENISH and i.status == IncidentStatus.OPEN),
            "assigned_count": sum(1 for i in incidents if i.status in ASSIGNEDISH),
            "resolved_count": sum(1 for i in incidents if i.status == IncidentStatus.RESOLVED),
            "cancelled_count": sum(1 for i in incidents if i.status == IncidentStatus.CANCELLED),
            "available_resources": sum(1 for r in resources if r.status == ResourceStatus.AVAILABLE),
            "busy_resources": sum(1 for r in resources if r.status == ResourceStatus.BUSY),
            "unread_notifications": unread,
            "redis_connected": bool(getattr(broker, "redis_connected", False)),
            "pubsub_mode": getattr(broker, "mode", "unknown"),
            "recent_incidents": [incident_out(i).model_dump(mode="json") for i in recent],
        }
    )
