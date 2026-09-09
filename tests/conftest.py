import os
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
(ROOT / "data").mkdir(parents=True, exist_ok=True)
_test_db = ROOT / "data" / "test_nexusone.db"
if _test_db.exists():
    try:
        _test_db.unlink()
    except OSError:
        pass
os.environ.setdefault("DATABASE_URL", f"sqlite:///{_test_db.as_posix()}")
os.environ.setdefault("SECRET_KEY", "test-secret-key-which-is-at-least-32-chars")
os.environ.setdefault("APP_SEED_PASSWORD", "ChangeMe123!")
os.environ.setdefault("SEED_DEMO_DATA", "true")
os.environ["NEXUSONE_TESTING"] = "1"
os.environ["REDIS_URL"] = "redis://127.0.0.1:1/0"
os.environ.setdefault("REDIS_OPTIONAL", "true")
os.environ.setdefault("CORS_ORIGINS", "http://localhost:3005")
