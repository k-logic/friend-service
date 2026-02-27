from datetime import datetime

from pydantic import BaseModel


class FootprintCreateRequest(BaseModel):
    persona_id: int


class FootprintResponse(BaseModel):
    id: int
    user_id: int
    persona_id: int
    created_at: datetime

    model_config = {"from_attributes": True}
