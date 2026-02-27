from datetime import datetime

from pydantic import BaseModel


class MessageSendRequest(BaseModel):
    session_id: int
    title: str | None = None
    content: str
    image_url: str | None = None


class MessageResponse(BaseModel):
    id: int
    session_id: int
    sender_type: str
    sender_id: int
    sender_display_name: str | None = None
    title: str | None
    content: str
    image_url: str | None
    credit_cost: int
    created_at: datetime

    model_config = {"from_attributes": True}


class MessagePollResponse(BaseModel):
    messages: list[MessageResponse]
    last_message_id: int | None
