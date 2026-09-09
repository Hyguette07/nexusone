from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.notification import Notification
from app.models.user import User
from app.models.enums import Role


def notify(db: Session, user_id: int, title: str, body: str, incident_id: int | None = None) -> Notification:
    row = Notification(
        user_id=user_id,
        title=title,
        body=body,
        incident_id=incident_id,
        created_at=datetime.now(timezone.utc),
    )
    db.add(row)
    return row


def notify_roles(
    db: Session,
    roles: list[Role],
    title: str,
    body: str,
    incident_id: int | None = None,
) -> None:
    users = db.query(User).filter(User.role.in_(roles), User.is_active.is_(True)).all()
    for user in users:
        notify(db, user.id, title, body, incident_id)
