from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.role import Role
from schemas.role import RoleCreate, RoleResponse

router = APIRouter(prefix="/roles", tags=["Roles"])


@router.post("/", response_model=RoleResponse)
def create_role(role_data: RoleCreate, db: Session = Depends(get_db)):
    existing = db.query(Role).filter(Role.name == role_data.name).first()
    if existing:
        raise HTTPException(status_code=400, detail="Role already exists")

    role = Role(
        name=role_data.name,
        description=role_data.description
    )

    db.add(role)
    db.commit()
    db.refresh(role)
    return role


@router.get("/", response_model=list[RoleResponse])
def get_roles(db: Session = Depends(get_db)):
    return db.query(Role).all()