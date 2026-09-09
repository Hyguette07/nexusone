export type Role = "CITIZEN" | "DISPATCHER" | "RESPONDER" | "ADMIN";

export type IncidentType = "FLOOD" | "MEDICAL" | "FIRE" | "MISSING_PERSON";
export type IncidentStatus = "OPEN" | "ASSIGNED" | "EN_ROUTE" | "ON_SCENE" | "RESOLVED" | "CANCELLED";
export type IncidentSeverity = "LOW" | "MEDIUM" | "HIGH" | "CRITICAL";
export type ResourceType = "CLINIC" | "BUS" | "SHELTER" | "VOLUNTEER_TEAM" | "FIRE_UNIT" | "AMBULANCE";
export type ResourceStatus = "AVAILABLE" | "BUSY" | "OFFLINE";
export type AssignmentStatus = "PENDING" | "ACCEPTED" | "EN_ROUTE" | "ON_SCENE" | "COMPLETED" | "DECLINED";

export type AuthUser = {
  token: string;
  user_id: number;
  email: string;
  role: Role;
  full_name: string;
};

export type Incident = {
  id: number;
  title: string;
  description: string;
  incident_type: IncidentType;
  status: IncidentStatus;
  severity: IncidentSeverity;
  latitude: number;
  longitude: number;
  location_name: string;
  reporter_id: number;
  reporter_name?: string | null;
  created_at: string;
  updated_at: string;
  resolved_at?: string | null;
  open_assignment_count: number;
};

export type Resource = {
  id: number;
  name: string;
  resource_type: ResourceType;
  capacity: number;
  current_load: number;
  latitude: number;
  longitude: number;
  location_name: string;
  status: ResourceStatus;
  contact_phone?: string | null;
  notes?: string | null;
  created_at: string;
};

export type RankedResource = {
  resource_id: number;
  name: string;
  resource_type: string;
  score: number;
  distance_km: number;
  type_match: number;
  capacity_score: number;
  availability_score: number;
  eligible: boolean;
  reasons: string[];
};

export type Assignment = {
  id: number;
  incident_id: number;
  resource_id: number;
  assigned_by_id: number;
  responder_id?: number | null;
  status: AssignmentStatus;
  notes?: string | null;
  ranker_score?: number | null;
  ranker_reason?: string | null;
  assigned_at: string;
  updated_at: string;
  incident_title?: string | null;
  resource_name?: string | null;
};

export type Dashboard = {
  open_count: number;
  assigned_count: number;
  resolved_count: number;
  cancelled_count: number;
  available_resources: number;
  busy_resources: number;
  unread_notifications: number;
  redis_connected: boolean;
  pubsub_mode: string;
  recent_incidents: Incident[];
};

export type AppNotification = {
  id: number;
  user_id: number;
  title: string;
  body: string;
  read: boolean;
  incident_id?: number | null;
  created_at: string;
};
