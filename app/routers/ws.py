import logging

from fastapi import APIRouter, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session, selectinload

from app.auth.security import decode_token
from app.database import SessionLocal
from app.models.enums import IncidentStatus
from app.models.incident import Incident
from app.models.user import User
from app.services.serializers import incident_payload

logger = logging.getLogger("nexusone.ws")
router = APIRouter()

LIVE_STATUSES = {
    IncidentStatus.OPEN,
    IncidentStatus.ASSIGNED,
    IncidentStatus.EN_ROUTE,
    IncidentStatus.ON_SCENE,
}


def _user_from_token(token: str | None, db: Session) -> User | None:
    if not token:
        return None
    try:
        payload = decode_token(token)
        return db.get(User, int(payload["sub"]))
    except (ValueError, KeyError, TypeError):
        return None


@router.websocket("/ws/incidents")
async def incidents_socket(websocket: WebSocket, token: str | None = Query(default=None)):
    db = SessionLocal()
    hub = None
    try:
        user = _user_from_token(token, db)
        if user is None or not user.is_active:
            await websocket.close(code=4401)
            return
        hub = websocket.app.state.hub
        broker = websocket.app.state.broker
        await hub.connect(websocket)
        open_rows = (
            db.query(Incident)
            .options(selectinload(Incident.reporter), selectinload(Incident.assignments))
            .filter(Incident.status.in_(LIVE_STATUSES))
            .order_by(Incident.created_at.desc())
            .all()
        )
        await websocket.send_json(
            {
                "event": "board.snapshot",
                "payload": {
                    "incidents": [incident_payload(r) for r in open_rows],
                    "pubsub_mode": broker.mode,
                    "disclaimer": "Educational simulation — not a 911 replacement.",
                },
            }
        )
    finally:
        db.close()

    if hub is None:
        return
    try:
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        pass
    except Exception:
        logger.exception("WebSocket error")
    finally:
        await hub.disconnect(websocket)
