from datetime import datetime

from pydantic import BaseModel, EmailStr


class InvitationCreateRequest(BaseModel):
    email: EmailStr


class InvitationResponse(BaseModel):
    id: int
    token: str
    invite_url: str
    email: str
    expires_at: datetime
    used_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InvitationVerifyResponse(BaseModel):
    email: str


class InvitationRegisterRequest(BaseModel):
    display_name: str
