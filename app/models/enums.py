import enum


class Role(str, enum.Enum):
    CITIZEN = "CITIZEN"
    DISPATCHER = "DISPATCHER"
    RESPONDER = "RESPONDER"
    ADMIN = "ADMIN"


class IncidentType(str, enum.Enum):
    FLOOD = "FLOOD"
    MEDICAL = "MEDICAL"
    FIRE = "FIRE"
    MISSING_PERSON = "MISSING_PERSON"


class IncidentStatus(str, enum.Enum):
    OPEN = "OPEN"
    ASSIGNED = "ASSIGNED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    RESOLVED = "RESOLVED"
    CANCELLED = "CANCELLED"


class IncidentSeverity(str, enum.Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"


class ResourceType(str, enum.Enum):
    CLINIC = "CLINIC"
    BUS = "BUS"
    SHELTER = "SHELTER"
    VOLUNTEER_TEAM = "VOLUNTEER_TEAM"
    FIRE_UNIT = "FIRE_UNIT"
    AMBULANCE = "AMBULANCE"


class ResourceStatus(str, enum.Enum):
    AVAILABLE = "AVAILABLE"
    BUSY = "BUSY"
    OFFLINE = "OFFLINE"


class AssignmentStatus(str, enum.Enum):
    PENDING = "PENDING"
    ACCEPTED = "ACCEPTED"
    EN_ROUTE = "EN_ROUTE"
    ON_SCENE = "ON_SCENE"
    COMPLETED = "COMPLETED"
    DECLINED = "DECLINED"
