from datetime import datetime

from pydantic import BaseModel, EmailStr


# --- ユーザ管理 ---
class AdminUserSearchParams(BaseModel):
    email: str | None = None
    display_name: str | None = None
    role: str | None = None
    status: str | None = None
    gender: str | None = None


class AdminUserCreateRequest(BaseModel):
    email: EmailStr
    display_name: str
    password: str
    role: str = "user"


class AdminUserResponse(BaseModel):
    id: int
    email: str
    display_name: str
    credit_balance: int
    role: str
    status: str
    avatar_url: str | None
    created_at: datetime

    model_config = {"from_attributes": True}


class AdminUserStatusUpdate(BaseModel):
    status: str


class UserCountByStatus(BaseModel):
    status: str
    count: int


# --- 問い合わせ ---
class InquiryResponse(BaseModel):
    id: int
    account_id: int
    account_display_name: str | None = None
    subject: str
    body: str
    status: str
    admin_reply: str | None
    replied_at: datetime | None
    created_at: datetime

    model_config = {"from_attributes": True}


class InquiryCreateRequest(BaseModel):
    subject: str
    body: str


class InquiryReplyRequest(BaseModel):
    admin_reply: str


# --- 有料情報 ---
class PaidContentCreateRequest(BaseModel):
    title: str
    description: str | None = None
    price: int
    is_active: bool = True


class PaidContentResponse(BaseModel):
    id: int
    title: str
    description: str | None
    price: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- メール配信 ---
class MailCampaignCreateRequest(BaseModel):
    type: str
    subject: str
    body: str
    target_filter: dict | None = None
    scheduled_at: datetime | None = None
    interval: str | None = None


class MailCampaignResponse(BaseModel):
    id: int
    type: str
    subject: str
    body: str
    target_filter: dict | None
    scheduled_at: datetime | None
    interval: str | None
    status: str
    created_at: datetime

    model_config = {"from_attributes": True}


class TriggerMailSettingCreateRequest(BaseModel):
    trigger_event: str
    mail_campaign_id: int
    delay_minutes: int = 0
    is_active: bool = True


class TriggerMailSettingResponse(BaseModel):
    id: int
    trigger_event: str
    mail_campaign_id: int
    delay_minutes: int
    is_active: bool
    created_at: datetime

    model_config = {"from_attributes": True}


# --- LINE Bot ---
class LineBotAccountCreateRequest(BaseModel):
    line_bot_id: str
    memo: str | None = None
    webhook_url: str | None = None
    is_active: bool = False


class LineBotAccountUpdateRequest(BaseModel):
    memo: str | None = None
    webhook_url: str | None = None
    is_active: bool | None = None


class LineBotAccountResponse(BaseModel):
    id: int
    line_bot_id: str
    memo: str | None
    webhook_url: str | None
    is_active: bool
    subscriber_count: int
    monthly_delivery_count: int
    created_at: datetime
    updated_at: datetime

    model_config = {"from_attributes": True}


# --- 年齢認証 ---
class AgeVerificationResponse(BaseModel):
    id: int
    account_id: int
    account_display_name: str | None = None
    status: str
    submitted_at: datetime
    reviewed_at: datetime | None
    reviewer_id: int | None

    model_config = {"from_attributes": True}


class AgeVerificationReviewRequest(BaseModel):
    status: str  # approved or rejected
