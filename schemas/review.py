from pydantic import BaseModel, ConfigDict, Field


class ReviewCreate(BaseModel):
    service_id: int
    rating: int = Field(ge=1, le=5)
    comment: str | None = None

class ReviewUpdate(BaseModel):
    rating: int = Field(ge=1, le=5)
    comment: str | None = None

class ReviewResponse(BaseModel):
    id: int
    service_id: int
    user_id: int
    rating: int
    comment: str | None = None

    model_config = ConfigDict(from_attributes=True)