"""NexusOne API — community emergency coordination (educational simulation)."""

from __future__ import annotations

import asyncio
import logging
import os
from contextlib import asynccontextmanager

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app import DISCLAIMER, __version__
from app.config import get_settings
from app.database import Base, SessionLocal, engine
from app.realtime.hub import ConnectionHub
from app.routers import assignments, auth, dashboard, incidents, notifications, resources, ws
from app.services.pubsub import InMemoryBroker, create_broker
from app.services.seed import seed_if_empty
from app.services.worker import run_worker

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(name)s %(message)s")
logger = logging.getLogger("nexusone")


@asynccontextmanager
async def lifespan(app: FastAPI):
    settings = get_settings()
    Base.metadata.create_all(bind=engine)
    db = SessionLocal()
    try:
        seed_if_empty(db)
    finally:
        db.close()

    app.state.hub = ConnectionHub()
    testing = os.environ.get("NEXUSONE_TESTING") == "1"
    pump = worker = None
    if testing:
        app.state.broker = InMemoryBroker()
    else:
        app.state.broker = await create_broker(settings.redis_url, optional=settings.redis_optional)

        async def pump_broker() -> None:
            async for message in app.state.broker.subscribe():
                await app.state.hub.broadcast(message)

        pump = asyncio.create_task(pump_broker())
        worker = asyncio.create_task(run_worker(app.state, settings.worker_interval_seconds))
    logger.info("NexusOne ready — pub/sub mode=%s testing=%s", app.state.broker.mode, testing)
    try:
        yield
    finally:
        tasks = [t for t in (worker, pump) if t is not None]
        for task in tasks:
            task.cancel()
        if tasks:
            try:
                await asyncio.wait_for(asyncio.gather(*tasks, return_exceptions=True), timeout=3)
            except asyncio.TimeoutError:
                logger.warning("Background tasks did not stop in time")
        try:
            await asyncio.wait_for(app.state.broker.close(), timeout=2)
        except (asyncio.TimeoutError, Exception):
            logger.warning("Broker close timed out or failed")
        engine.dispose()


settings = get_settings()
app = FastAPI(
    title="NexusOne",
    description=(
        "Real-time multi-domain emergency dispatch for a city. "
        f"{DISCLAIMER} Interactive docs at `/docs`."
    ),
    version=__version__,
    docs_url="/docs",
    redoc_url="/redoc",
    lifespan=lifespan,
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origin_list,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/health")
def health():
    broker = getattr(app.state, "broker", None)
    return {
        "status": "ok",
        "service": "nexusone",
        "version": __version__,
        "pubsub_mode": getattr(broker, "mode", "starting"),
        "disclaimer": DISCLAIMER,
    }


app.include_router(auth.router, prefix="/api/v1")
app.include_router(incidents.router, prefix="/api/v1")
app.include_router(resources.router, prefix="/api/v1")
app.include_router(assignments.router, prefix="/api/v1")
app.include_router(dashboard.router, prefix="/api/v1")
app.include_router(notifications.router, prefix="/api/v1")
app.include_router(ws.router)
