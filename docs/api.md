# NexusOne — API

Base URL: `http://localhost:8085`

Interactive OpenAPI: [http://localhost:8085/docs](http://localhost:8085/docs)

Every JSON envelope includes a `disclaimer` field. **Educational simulation — not a 911 replacement.**

```json
{
  "success": true,
  "message": "ok",
  "data": {},
  "disclaimer": "Educational simulation — not a real 911 or emergency-services replacement. In a real emergency, call official services."
}
```

Auth header: `Authorization: Bearer <jwt>`

## Health

`GET /health` — public. Includes `pubsub_mode` (`redis` or `memory`).

## Auth

| Method | Path | Who |
| --- | --- | --- |
| POST | `/api/v1/auth/register` | Public. Always creates `CITIZEN`. |
| POST | `/api/v1/auth/login` | Public |
| GET | `/api/v1/auth/me` | Authenticated |
| GET | `/api/v1/auth/system` | Authenticated. Redis vs memory, WS client count |

Register body: `{ "email", "password", "full_name", "phone?" }`  
Login body: `{ "email", "password" }`  
Token payload: `{ "token", "user_id", "email", "role", "full_name" }`

## Incidents

| Method | Path | Who |
| --- | --- | --- |
| GET | `/api/v1/incidents` | Authenticated. Query `status`, `type`, `severity` |
| POST | `/api/v1/incidents` | Authenticated |
| GET | `/api/v1/incidents/{id}` | Authenticated |
| PATCH | `/api/v1/incidents/{id}` | Citizen: cancel own. Dispatcher/Admin: status/severity |
| GET | `/api/v1/incidents/{id}/rankings` | Dispatcher, Admin, Responder |

Create body:

```json
{
  "title": "Nyabugogo drainage overflow",
  "description": "Knee-deep water at the taxi park.",
  "incident_type": "FLOOD",
  "severity": "HIGH",
  "latitude": -1.9397,
  "longitude": 30.0444,
  "location_name": "Nyabugogo bus park"
}
```

Rankings return DispatchRanker rows: `score`, `distance_km`, `reasons[]`, `eligible`.

## Resources

| Method | Path | Who |
| --- | --- | --- |
| GET | `/api/v1/resources` | Authenticated. Query `type`, `status` |
| POST | `/api/v1/resources` | Dispatcher, Admin |
| GET | `/api/v1/resources/{id}` | Authenticated |
| PATCH | `/api/v1/resources/{id}` | Dispatcher, Admin, Responder |

## Assignments

| Method | Path | Who |
| --- | --- | --- |
| GET | `/api/v1/assignments` | Role-scoped |
| POST | `/api/v1/assignments` | Dispatcher, Admin `{ incident_id, resource_id, notes? }` |
| GET | `/api/v1/assignments/{id}` | Authenticated |
| PATCH | `/api/v1/assignments/{id}` | Responder (own), Dispatcher, Admin — `{ status, notes? }` |

Assigning a resource snapshots `ranker_score` / `ranker_reason`, bumps `current_load`, and may mark the resource `BUSY`. Completing an assignment decrements load and can resolve the incident.

## Dashboard

`GET /api/v1/dashboard` — `open_count`, `assigned_count`, `resolved_count`, resource availability, unread notifications, `pubsub_mode`, recent incidents.

## Notifications

`GET /api/v1/notifications`  
`PATCH /api/v1/notifications/{id}/read`

## WebSocket

`WS /ws/incidents?token=<jwt>`

Events:

| event | payload |
| --- | --- |
| `board.snapshot` | Current live incidents + `pubsub_mode` |
| `incident.created` | Incident |
| `incident.updated` | Incident |
| `incident.resolved` | Incident |
| `assignment.created` | Assignment |
| `assignment.updated` | Assignment |
| `dispatch.suggestion` | Worker ranking hints for unassigned OPEN incidents |

If Redis is down, the API still serves REST and uses an in-memory broker so a single-process demo board updates. See [architecture.md](./architecture.md).
