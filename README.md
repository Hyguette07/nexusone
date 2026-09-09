# NexusOne

![Python](https://img.shields.io/badge/Python-3.12-blue)
![FastAPI](https://img.shields.io/badge/FastAPI-0.115-teal)
![Next.js](https://img.shields.io/badge/Next.js-14-black)
![Redis](https://img.shields.io/badge/Redis-7-red)

Real-time multi-domain emergency dispatch for a city: incidents, nearby resources, dispatcher assignment, and a live map board over WebSockets.

**Educational simulation — not a 911 or emergency-services replacement.** In a real emergency, call official services. The disclaimer is on the API envelope, OpenAPI description, and every UI surface.

## Problem

A flood at Nyabugogo, a fire in Nyamirambo, a medical collapse at a hospital gate, and a missing-person report at Kimironko do not share a board. Clinics, buses, shelters, and volunteer teams sit in separate phone trees. Dispatchers guess which unit is closest and still available.

## Solution

NexusOne is a community coordination desk:

- Citizens report incidents (flood, medical, fire, missing person)
- Dispatchers see a live board and assign a resource
- Responders update status (accepted → en route → on scene → completed)
- **DispatchRanker** scores which resource should respond: distance, type match, remaining capacity, already-busy / offline

Seed data is Kigali-flavoured (coordinates around `-1.95, 30.06`).

## Features

- JWT auth with roles: Citizen, Dispatcher, Responder, Admin
- Incident report, list, filter, and status updates
- Resource catalog (clinics, buses, shelters, volunteer teams, fire units, ambulances)
- Dispatcher assignment with a ranked recommendation list
- WebSocket `/ws/incidents` live board (Redis pub/sub, in-memory fallback if Redis is down)
- In-app notifications
- Dashboard counts: open / assigned / resolved
- Schematic city map of pins — no Google Maps key
- OpenAPI at `/docs`

## Architecture

See [docs/architecture.md](./docs/architecture.md).

```
Next.js UI  →  FastAPI  →  SQLite
                 ↓
         Redis pub/sub (optional)
                 ↓
           WebSocket hub
```

REST works without Redis. Multi-instance live boards need Redis. Locally, an in-memory broker keeps the demo working.

## Technology stack

Frontend: Next.js 14.2, React, TypeScript, Tailwind CSS  
Backend: Python 3.12, FastAPI, SQLAlchemy 2, python-jose, passlib/bcrypt  
Data: SQLite (`./data/nexusone.db`) locally; Redis for pub/sub  
Delivery: Docker Compose, GitHub Actions

## Database

[docs/database.md](./docs/database.md)

## API documentation

[docs/api.md](./docs/api.md) and interactive Swagger at http://localhost:8085/docs when the API is running.

## Installation

```bash
cp .env.example .env
```

Python 3.12 and Node 22 are required. Redis is optional for a single-process demo.

## Environment variables

See `.env.example`. Never commit `.env`. Demo seed password is `APP_SEED_PASSWORD` (default `ChangeMe123!`).

Seeded accounts (local/demo only):

| Role | Email | Password |
| --- | --- | --- |
| Citizen | citizen@nexusone.local | `APP_SEED_PASSWORD` |
| Dispatcher | dispatcher@nexusone.local | `APP_SEED_PASSWORD` |
| Responder | responder@nexusone.local | `APP_SEED_PASSWORD` |
| Admin | admin@nexusone.local | `APP_SEED_PASSWORD` |

## Running locally

API (SQLite, port 8085):

```bash
python -m venv .venv
.venv\Scripts\activate
pip install -r requirements.txt
uvicorn app.main:app --reload --port 8085
```

If Redis is not running, the API logs a warning and uses in-memory pub/sub. REST still works; the live board works inside that one API process.

UI (port 3005):

```bash
cd frontend
copy ..\.env.example .env.local
npm install
npm run dev
```

Open http://localhost:3005 — log in as `dispatcher@nexusone.local`.

## Testing

```bash
pytest
cd frontend && npm test -- --run
```

See [tests/README.md](./tests/README.md). `DispatchRanker` is covered without Redis.

## Docker

```bash
docker compose up --build
```

Starts Redis, the API on 8085, and the web UI on 3005.

## Deployment

[docs/deployment.md](./docs/deployment.md)

## Future improvements

PostgreSQL + Alembic for production, SMS/USSD citizen reporting, multi-city geofences, and a dedicated worker process instead of an in-process asyncio loop.

## Lessons learned

[docs/lessons-learned.md](./docs/lessons-learned.md)

## Author

Isimbi Hyguette — Hyguette Labs  
isimbihyguette07@gmail.com

## License

MIT. See [LICENSE](./LICENSE).
