from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import AssignmentStatus


class AssignmentCreate(BaseModel):
    incident_id: int
    resource_id: int
    notes: str | None = Field(default=None, max_length=2000)


class AssignmentUpdate(BaseModel):
    status: AssignmentStatus | None = None
    notes: str | None = Field(default=None, max_length=2000)


class AssignmentOut(BaseModel):
    id: int
    incident_id: int
    resource_id: int
    assigned_by_id: int
    responder_id: int | None
    status: AssignmentStatus
    notes: str | None
    ranker_score: float | None
    ranker_reason: str | None
    assigned_at: datetime
    updated_at: datetime
    incident_title: str | None = None
    resource_name: str | None = None

    model_config = {"from_attributes": True}
