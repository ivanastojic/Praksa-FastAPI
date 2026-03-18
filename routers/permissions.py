from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.permission import Permission
from schemas.permission import PermissionCreate, PermissionResponse

router = APIRouter(prefix="/permissions", tags=["Permissions"])


@router.post("/", response_model=PermissionResponse)
def create_permission(permission_data: PermissionCreate, db: Session = Depends(get_db)):
    existing = db.query(Permission).filter(Permission.name == permission_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Permission already exists")

    permission = Permission(
        name=permission_data.name,
        description=permission_data.description
    )

    db.add(permission)
    db.commit()
    db.refresh(permission)
    return permission


@router.get("/", response_model=list[PermissionResponse])
def get_permissions(db: Session = Depends(get_db)):
    return db.query(Permission).all()