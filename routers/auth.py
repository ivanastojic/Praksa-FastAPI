from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from database.connection import get_db
from models.user import User
from schemas.user import UserCreate, UserResponse
from schemas.auth import LoginRequest, TokenResponse
from utils.security import hash_password, verify_password, create_access_token, decode_access_token
from fastapi.security import OAuth2PasswordBearer, OAuth2PasswordRequestForm
from models.role import Role
from models.permission import Permission
from models.role_permission import RolePermission

router = APIRouter(prefix="/auth", tags=["Auth"])

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


@router.post("/register", response_model=UserResponse)
def register(user_data: UserCreate, db: Session = Depends(get_db)):
    existing_user = db.query(User).filter(User.email == user_data.email).first()
    if existing_user:
        raise HTTPException(status_code=400, detail="Email already exists")

    allowed_roles = ["client", "provider"]

    if user_data.role_name not in allowed_roles:
        raise HTTPException(
            status_code=400,
            detail="You can only register as client or provider"
        )

    selected_role = db.query(Role).filter(Role.name == user_data.role_name).first()
    if not selected_role:
        raise HTTPException(status_code=404, detail=f"Role '{user_data.role_name}' not found")

    new_user = User(
        full_name=user_data.full_name,
        email=user_data.email,
        password_hash=hash_password(user_data.password),
        phone_number=user_data.phone_number,
        role_id=selected_role.id
    )

    db.add(new_user)
    db.commit()
    db.refresh(new_user)
    return new_user


@router.post("/login", response_model=TokenResponse)
def login(form_data: OAuth2PasswordRequestForm = Depends(), db: Session = Depends(get_db)):
    user = db.query(User).filter(User.email == form_data.username).first()

    if not user or not verify_password(form_data.password, user.password_hash):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid email or password"
        )

    access_token = create_access_token({"sub": str(user.id)})
    return {"access_token": access_token, "token_type": "bearer"}

def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: Session = Depends(get_db)
):
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(status_code=401, detail="Invalid or expired token")

    user = db.query(User).filter(User.id == int(payload["sub"])).first()
    if not user:
        raise HTTPException(status_code=401, detail="User not found")

    return user


@router.get("/me", response_model=UserResponse)
def read_me(current_user: User = Depends(get_current_user)):
    return current_user

def get_user_role_name(current_user: User, db: Session) -> str | None:
    role = db.query(Role).filter(Role.id == current_user.role_id).first()
    return role.name if role else None


def require_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role_name = get_user_role_name(current_user, db)
    if role_name != "admin":
        raise HTTPException(status_code=403, detail="Admin access required")
    return current_user


def require_provider_or_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role_name = get_user_role_name(current_user, db)
    if role_name not in ["admin", "provider"]:
        raise HTTPException(status_code=403, detail="Provider or admin access required")
    return current_user


def require_client_or_provider_or_admin(
    current_user: User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    role_name = get_user_role_name(current_user, db)
    if role_name not in ["admin", "provider", "client"]:
        raise HTTPException(status_code=403, detail="Access denied")
    return current_user

def get_user_permissions(current_user: User, db: Session) -> list[str]:
    if not current_user.role_id:
        return []

    permissions = (
        db.query(Permission.name)
        .join(RolePermission, Permission.id == RolePermission.permission_id)
        .filter(RolePermission.role_id == current_user.role_id)
        .all()
    )

    return [permission[0] for permission in permissions]


def has_permission(current_user: User, permission_name: str, db: Session) -> bool:
    user_permissions = get_user_permissions(current_user, db)
    return permission_name in user_permissions

def require_permission(permission_name: str):
    def permission_checker(
        current_user: User = Depends(get_current_user),
        db: Session = Depends(get_db)
    ):
        if not has_permission(current_user, permission_name, db):
            raise HTTPException(
                status_code=403,
                detail=f"Permission '{permission_name}' required"
            )
        return current_user

    return permission_checker