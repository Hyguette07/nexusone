from datetime import datetime

from pydantic import BaseModel, Field

from app.models.enums import ResourceStatus, ResourceType


class ResourceCreate(BaseModel):
    name: str = Field(min_length=2, max_length=200)
    resource_type: ResourceType
    capacity: int = Field(default=1, ge=1, le=5000)
    current_load: int = Field(default=0, ge=0, le=5000)
    latitude: float = Field(ge=-90, le=90)
    longitude: float = Field(ge=-180, le=180)
    location_name: str = Field(min_length=2, max_length=200)
    status: ResourceStatus = ResourceStatus.AVAILABLE
    contact_phone: str | None = Field(default=None, max_length=40)
    notes: str | None = Field(default=None, max_length=2000)


class ResourceUpdate(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=200)
    capacity: int | None = Field(default=None, ge=1, le=5000)
    current_load: int | None = Field(default=None, ge=0, le=5000)
    status: ResourceStatus | None = None
    location_name: str | None = Field(default=None, min_length=2, max_length=200)
    contact_phone: str | None = None
    notes: str | None = None
    latitude: float | None = Field(default=None, ge=-90, le=90)
    longitude: float | None = Field(default=None, ge=-180, le=180)


class ResourceOut(BaseModel):
    id: int
    name: str
    resource_type: ResourceType
    capacity: int
    current_load: int
    latitude: float
    longitude: float
    location_name: str
    status: ResourceStatus
    contact_phone: str | None
    notes: str | None
    created_at: datetime

    model_config = {"from_attributes": True}
