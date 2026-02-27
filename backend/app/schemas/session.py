from datetime import datetime

from pydantic import BaseModel


class SessionCreateRequest(BaseModel):
    persona_id: int


class SessionResponse(BaseModel):
    id: int
    user_id: int
    user_display_name: str | None = None
    user_avatar_url: str | None = None
    persona_id: int
    persona_name: str | None = None
    persona_avatar_url: str | None = None
    status: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
