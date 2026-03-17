from pydantic import BaseModel, ConfigDict



class ServiceCreate(BaseModel):
    title: str
    description: str | None = None
    price: float
    category_id: int


class ServiceUpdate(BaseModel):
    title: str
    description: str | None = None
    price: float
    category_id: int


class ServiceResponse(BaseModel):
    id: int
    title: str
    description: str | None = None
    price: float
    category_id: int
    provider_id: int

    model_config = ConfigDict(from_attributes=True)
