from datetime import datetime

from pydantic import BaseModel


class LikeRequest(BaseModel):
    persona_id: int


class LikeResponse(BaseModel):
    id: int
    user_account_id: int
    persona_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
