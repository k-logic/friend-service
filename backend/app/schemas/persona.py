from datetime import date, datetime

from pydantic import BaseModel


class PersonaCreateRequest(BaseModel):
    name: str
    gender: str | None = None
    age: int | None = None
    avatar_url: str | None = None
    bio: str | None = None
    attributes: dict | None = None
    registered_at: date | None = None


class PersonaUpdateRequest(BaseModel):
    name: str | None = None
    gender: str | None = None
    age: int | None = None
    avatar_url: str | None = None
    bio: str | None = None
    attributes: dict | None = None
    is_active: bool | None = None
    registered_at: date | None = None


class PersonaResponse(BaseModel):
    id: int
    staff_id: int
    name: str
    gender: str | None
    age: int | None
    avatar_url: str | None
    bio: str | None
    attributes: dict | None
    registered_at: date | None
    is_active: bool
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
