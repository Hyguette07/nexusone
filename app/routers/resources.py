from fastapi import APIRouter, Depends, HTTPException, Query, status
from sqlalchemy.orm import Session

from app.auth.deps import get_current_user, require_roles
from app.database import get_db
from app.models.enums import ResourceStatus, ResourceType, Role
from app.models.resource import Resource
from app.models.user import User
from app.schemas.common import ok
from app.schemas.resource import ResourceCreate, ResourceOut, ResourceUpdate

router = APIRouter(prefix="/resources", tags=["resources"])


@router.get("")
def list_resources(
    db: Session = Depends(get_db),
    _: User = Depends(get_current_user),
    resource_type: ResourceType | None = Query(default=None, alias="type"),
    status_filter: ResourceStatus | None = Query(default=None, alias="status"),
):
    q = db.query(Resource)
    if resource_type:
        q = q.filter(Resource.resource_type == resource_type)
    if status_filter:
        q = q.filter(Resource.status == status_filter)
    rows = q.order_by(Resource.name.asc()).all()
    return ok([ResourceOut.model_validate(r).model_dump(mode="json") for r in rows])


@router.post("", status_code=status.HTTP_201_CREATED)
def create_resource(
    body: ResourceCreate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.DISPATCHER, Role.ADMIN)),
):
    row = Resource(**body.model_dump())
    db.add(row)
    db.commit()
    db.refresh(row)
    return ok(ResourceOut.model_validate(row).model_dump(mode="json"), "Resource added")


@router.get("/{resource_id}")
def get_resource(resource_id: int, db: Session = Depends(get_db), _: User = Depends(get_current_user)):
    row = db.get(Resource, resource_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    return ok(ResourceOut.model_validate(row).model_dump(mode="json"))


@router.patch("/{resource_id}")
def update_resource(
    resource_id: int,
    body: ResourceUpdate,
    db: Session = Depends(get_db),
    _: User = Depends(require_roles(Role.DISPATCHER, Role.ADMIN, Role.RESPONDER)),
):
    row = db.get(Resource, resource_id)
    if row is None:
        raise HTTPException(status_code=404, detail="Resource not found")
    for key, value in body.model_dump(exclude_unset=True).items():
        setattr(row, key, value)
    db.commit()
    db.refresh(row)
    return ok(ResourceOut.model_validate(row).model_dump(mode="json"))
