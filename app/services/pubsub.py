"""Pub/sub broker: Redis when available, in-memory fallback so the demo still runs."""

from __future__ import annotations

import asyncio
import json
import logging
from collections.abc import AsyncIterator
from typing import Any, Protocol

logger = logging.getLogger("nexusone.pubsub")

CHANNEL = "nexusone.incidents"


class Broker(Protocol):
    mode: str
    redis_connected: bool

    async def publish(self, message: dict[str, Any], channel: str = CHANNEL) -> None: ...
    def subscribe(self, channel: str = CHANNEL) -> AsyncIterator[dict[str, Any]]: ...
    async def close(self) -> None: ...


class InMemoryBroker:
    mode = "memory"
    redis_connected = False

    def __init__(self) -> None:
        self._subs: list[asyncio.Queue[dict[str, Any]]] = []
        self._lock = asyncio.Lock()

    async def publish(self, message: dict[str, Any], channel: str = CHANNEL) -> None:
        async with self._lock:
            targets = list(self._subs)
        for queue in targets:
            try:
                queue.put_nowait(message)
            except asyncio.QueueFull:
                try:
                    queue.get_nowait()
                except asyncio.QueueEmpty:
                    pass
                queue.put_nowait(message)

    async def subscribe(self, channel: str = CHANNEL) -> AsyncIterator[dict[str, Any]]:
        queue: asyncio.Queue[dict[str, Any]] = asyncio.Queue(maxsize=256)
        async with self._lock:
            self._subs.append(queue)
        try:
            while True:
                yield await queue.get()
        finally:
            async with self._lock:
                if queue in self._subs:
                    self._subs.remove(queue)

    async def close(self) -> None:
        async with self._lock:
            self._subs.clear()


class RedisBroker:
    mode = "redis"
    redis_connected = True

    def __init__(self, redis_client: Any) -> None:
        self._redis = redis_client

    async def publish(self, message: dict[str, Any], channel: str = CHANNEL) -> None:
        await self._redis.publish(channel, json.dumps(message, default=str))

    async def subscribe(self, channel: str = CHANNEL) -> AsyncIterator[dict[str, Any]]:
        pubsub = self._redis.pubsub()
        await pubsub.subscribe(channel)
        try:
            async for raw in pubsub.listen():
                if raw is None:
                    continue
                if raw.get("type") != "message":
                    continue
                data = raw.get("data")
                if isinstance(data, bytes):
                    data = data.decode("utf-8")
                try:
                    yield json.loads(data)
                except json.JSONDecodeError:
                    logger.warning("Dropped non-JSON Redis message")
        finally:
            await pubsub.unsubscribe(channel)
            await pubsub.aclose()

    async def close(self) -> None:
        await self._redis.aclose()


async def create_broker(redis_url: str, optional: bool = True) -> Broker:
    try:
        from redis.asyncio import Redis

        client = Redis.from_url(redis_url, decode_responses=True)
        await asyncio.wait_for(client.ping(), timeout=1.5)
        logger.info("Redis pub/sub connected at %s", redis_url)
        return RedisBroker(client)
    except Exception as exc:  # Redis missing, refused, or timeout
        if not optional:
            raise
        logger.warning("Redis unavailable (%s) — using in-memory pub/sub fallback", exc)
        return InMemoryBroker()
