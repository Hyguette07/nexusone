from fastapi import APIRouter, Depends, HTTPException, Request, status
from sqlalchemy import select
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user
from app.auth.security import create_access_token, hash_password, verify_password
from app.database import get_db
from app.models.enums import Role
from app.models.user import User
from app.schemas.auth import LoginIn, RegisterIn, TokenUser, UserOut
from app.schemas.common import ok

router = APIRouter(prefix="/auth", tags=["auth"])


@router.post("/register")
def register(body: RegisterIn, db: Session = Depends(get_db)):
    existing = db.scalar(select(User).where(User.email == body.email.lower()))
    if existing:
        raise HTTPException(status_code=status.HTTP_409_CONFLICT, detail="Email already registered")
    user = User(
        email=body.email.lower(),
        hashed_password=hash_password(body.password),
        full_name=body.full_name,
        phone=body.phone,
        role=Role.CITIZEN,
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    token = create_access_token(sub=str(user.id), role=user.role.value)
    return ok(
        TokenUser(
            token=token,
            user_id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name,
        ).model_dump(),
        "Registered. Educational simulation — not a 911 replacement.",
    )


@router.post("/login")
def login(body: LoginIn, db: Session = Depends(get_db)):
    user = db.scalar(select(User).where(User.email == body.email.lower()))
    if user is None or not verify_password(body.password, user.hashed_password):
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid email or password")
    if not user.is_active:
        raise HTTPException(status_code=status.HTTP_403_FORBIDDEN, detail="Account disabled")
    token = create_access_token(sub=str(user.id), role=user.role.value)
    return ok(
        TokenUser(
            token=token,
            user_id=user.id,
            email=user.email,
            role=user.role,
            full_name=user.full_name,
        ).model_dump(),
        "Signed in",
    )


@router.get("/me")
def me(user: User = Depends(get_current_user)):
    return ok(UserOut.model_validate(user).model_dump(mode="json"))


@router.get("/system")
def system_status(request: Request, _: User = Depends(get_current_user)):
    broker = getattr(request.app.state, "broker", None)
    return ok(
        {
            "pubsub_mode": getattr(broker, "mode", "unknown"),
            "redis_connected": bool(getattr(broker, "redis_connected", False)),
            "ws_clients": getattr(request.app.state.hub, "size", 0) if hasattr(request.app.state, "hub") else 0,
        }
    )
