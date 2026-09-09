# NexusOne — Deployment

## Local (no Docker)

1. Copy `.env.example` to `.env`. Set `SECRET_KEY` to a long random value.
2. Python 3.12: `python -m venv .venv` then `pip install -r requirements.txt`.
3. `uvicorn app.main:app --host 0.0.0.0 --port 8085`
4. Frontend: `cd frontend && npm install && npm run dev` (port 3005).
5. Redis is optional. Without it the API logs a warning and uses in-memory pub/sub. REST continues. The live board works for that one process.

## Docker Compose

```bash
docker compose up --build
```

Services: Redis 7, API 8085, web 3005. SQLite lives in the `nexusone_data` volume.

Set `SECRET_KEY` and `APP_SEED_PASSWORD` in `.env` before any environment that is not a laptop demo.

## Production notes

- Terminate TLS at a reverse proxy (Caddy, nginx, or a cloud load balancer). Serve the UI over HTTPS and the WebSocket over WSS.
- Replace SQLite with PostgreSQL (`DATABASE_URL=postgresql+psycopg://…`) and introduce Alembic migrations before any real traffic. `create_all` is a demo shortcut.
- Run **more than one API replica only if Redis is highly available**. The in-memory broker does not cross processes.
- Extract `run_worker` to a dedicated process if the suggestion loop must survive API deploys independently.
- Rotate `SECRET_KEY`. Never commit `.env`.
- Restrict `CORS_ORIGINS` to the real UI origin.
- This product is a **simulation**. Do not present it as a public emergency number, CAD, or 911 replacement. Keep the disclaimer on every public page.

## GitHub Actions

`.github/workflows/ci.yml` runs `pytest` on Python 3.12 and `npm run lint`, `npm test -- --run`, `npm run build` on Node 22.

## Health

`GET /health` should return `status: ok`. `pubsub_mode` is `redis` or `memory`.
