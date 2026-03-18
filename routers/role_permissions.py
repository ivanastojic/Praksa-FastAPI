from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from database.connection import get_db
from models.role import Role
from models.permission import Permission
from models.role_permission import RolePermission
from schemas.role_permission import RolePermissionCreate

router = APIRouter(prefix="/role-permissions", tags=["RolePermissions"])


@router.post("/")
def assign_permission_to_role(data: RolePermissionCreate, db: Session = Depends(get_db)):
    role = db.query(Role).filter(Role.id == data.role_id).first()
    if not role:
        raise HTTPException(status_code=404, detail="Role not found")

    permission = db.query(Permission).filter(Permission.id == data.permission_id).first()
    if not permission:
        raise HTTPException(status_code=404, detail="Permission not found")

    existing = db.query(RolePermission).filter(
        RolePermission.role_id == data.role_id,
        RolePermission.permission_id == data.permission_id
    ).first()

    if existing:
        raise HTTPException(status_code=400, detail="This permission is already assigned to the role")

    role_permission = RolePermission(
        role_id=data.role_id,
        permission_id=data.permission_id
    )

    db.add(role_permission)
    db.commit()

    return {"message": "Permission assigned to role successfully"}