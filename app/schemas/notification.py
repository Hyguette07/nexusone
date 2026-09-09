from datetime import datetime

from pydantic import BaseModel


class NotificationOut(BaseModel):
    id: int
    user_id: int
    title: str
    body: str
    read: bool
    incident_id: int | None
    created_at: datetime

    model_config = {"from_attributes": True}
