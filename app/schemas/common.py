from typing import Any, Generic, TypeVar

from pydantic import BaseModel

T = TypeVar("T")

DISCLAIMER = (
    "Educational simulation — not a real 911 or emergency-services replacement. "
    "In a real emergency, call official services."
)


class Envelope(BaseModel, Generic[T]):
    success: bool = True
    message: str = "ok"
    data: T | None = None
    disclaimer: str = DISCLAIMER


def ok(data: Any, message: str = "ok") -> dict[str, Any]:
    return {"success": True, "message": message, "data": data, "disclaimer": DISCLAIMER}


def fail(message: str, error: str | None = None) -> dict[str, Any]:
    return {
        "success": False,
        "message": message,
        "error": error,
        "data": None,
        "disclaimer": DISCLAIMER,
    }
