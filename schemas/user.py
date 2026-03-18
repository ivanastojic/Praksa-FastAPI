from pydantic import BaseModel, EmailStr, ConfigDict


class UserCreate(BaseModel):
    full_name: str
    email: EmailStr
    password: str
    phone_number: str | None = None
    role_name: str

class UserResponse(BaseModel):
    id: int
    full_name: str
    email: EmailStr
    phone_number: str | None = None
    role_name: str | None = None

    model_config = ConfigDict(from_attributes=True)

class UserRoleUpdate(BaseModel):
    role_id: int