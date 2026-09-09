from pydantic import BaseModel


class DashboardOut(BaseModel):
    open_count: int
    assigned_count: int
    resolved_count: int
    cancelled_count: int
    available_resources: int
    busy_resources: int
    unread_notifications: int
    redis_connected: bool
    pubsub_mode: str
    recent_incidents: list[dict]
