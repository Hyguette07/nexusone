"""NexusOne tests.

Run from the project root:

```
.venv\\Scripts\\python -m pytest
```

`DispatchRanker` is a pure function (distance, type match, capacity, busy/offline). Those tests do not need Redis or a running API.

API tests use SQLite and the in-memory pub/sub fallback.
"""
