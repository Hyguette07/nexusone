# NexusOne — Lessons learned

## Redis is a live-board concern, not a REST concern

The first instinct was “the stack includes Redis, so the API should fail without it.” That would have made the laptop demo fragile. Splitting the contract helped: REST and SQLite never talk to Redis; only the pub/sub path does. An in-memory broker keeps `/ws/incidents` honest on one process. The cost is operational: you must not scale the API horizontally without Redis, and that has to be written down, not discovered in production.

## DispatchRanker had to stay pure

The memorable capability is a ranking function. The moment it imported a SQLAlchemy session, tests would have needed a database and seed data. Keeping `RankableIncident` / `RankableResource` as dataclasses meant pytest could pin “type match beats a closer mismatch” and “busy ranks below available” without FastAPI. The HTTP layer only snapshots `ranker_score` onto the assignment so a later reader can see *why* that unit was chosen.

## WebSocket auth is a query parameter on purpose

Browsers cannot set an `Authorization` header on `new WebSocket(url)`. The token therefore travels as `?token=`. That is a leak into access logs and should be treated as such: short-lived JWTs, HTTPS/WSS, no tokens in README screenshots.

## SQLite `create_all` is a demo lie you must name

It is the fastest way to a file-backed local database. It is also how schemas drift. The docs say PostgreSQL + Alembic for production so a reviewer does not think the author forgot migrations — they were deferred on purpose.

## A schematic map is more honest than a missing API key

Requiring Google Maps would have blocked the first run. Projecting Kigali WGS84 onto a labelled SVG is less pretty than tiles and more reliable in a portfolio clone. Pins still move when incidents do, which is the behaviour that matters for the story.

## In-process workers are not Celery

The suggestion loop is an asyncio task on the API lifespan. That is enough to show “ranking can happen off the request.” It is not enough for retry, concurrency limits, or surviving a rolling deploy. Document the shortcut; do not hide it behind a “background workers” badge.

## Disclaimer is a product requirement

Emergency-adjacent UX without a disclaimer is how a demo gets screenshotted into a false claim. The copy is on the envelope, `/docs`, the landing page, the board, and the map. That repetition is intentional.
