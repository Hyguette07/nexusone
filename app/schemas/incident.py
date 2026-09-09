from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import IncidentSeverity, IncidentStatus, IncidentType


class IncidentCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=8, max_length=4000)
    incident_type: IncidentType
    severity: IncidentSeverity = IncidentSeverity.MEDIUM
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_name: str = Field(min_length=2, max_length=200)


class IncidentUpdate(BaseModel):
    title: str | None = Field(default=None, min_length=3, max_length=200)
    description: str | None = Field(default=None, min_length=8, max_length=4000)
    status: IncidentStatus | None = None
    severity: IncidentSeverity | None = None
    location_name: str | None = Field(default=None, min_length=2, max_length=200)


class IncidentOut(BaseModel):
    id: int
    title: str
    description: str
    incident_type: IncidentType
    status: IncidentStatus
    severity: IncidentSeverity
    latitude: float
    longitude: float
    location_name: str
    reporter_id: int
    reporter_name: str | None = None
    created_at: datetime
    updated_at: datetime
    resolved_at: datetime | None
    open_assignment_count: int = 0

    model_config = {"from_attributes": True}


class RankedResourceOut(BaseModel):
    resource_id: int
    name: str
    resource_type: str
    score: float
    distance_km: float
    type_match: float
    capacity_score: float
    availability_score: float
    eligible: bool
    reasons: list[str]
