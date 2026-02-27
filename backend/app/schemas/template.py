from datetime import datetime

from pydantic import BaseModel


class TemplateCreateRequest(BaseModel):
    label: str
    content: str


class TemplateUpdateRequest(BaseModel):
    label: str | None = None
    content: str | None = None


class TemplateResponse(BaseModel):
    id: int
    staff_account_id: int
    label: str
    content: str
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}
