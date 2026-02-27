import enum
from datetime import datetime

from sqlalchemy import Integer, String, Text, Enum, DateTime, Boolean, ForeignKey, func
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class CampaignType(str, enum.Enum):
    blast = "blast"
    scheduled = "scheduled"
    periodic = "periodic"
    trigger = "trigger"


class CampaignStatus(str, enum.Enum):
    draft = "draft"
    scheduled = "scheduled"
    sent = "sent"
    active = "active"


class MailCampaign(Base):
    __tablename__ = "mail_campaigns"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    type: Mapped[CampaignType] = mapped_column(Enum(CampaignType), nullable=False)
    subject: Mapped[str] = mapped_column(String(200), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    target_filter: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
    scheduled_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    interval: Mapped[str | None] = mapped_column(String(50), nullable=True)
    status: Mapped[CampaignStatus] = mapped_column(Enum(CampaignStatus), default=CampaignStatus.draft, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())


class TriggerMailSetting(Base):
    __tablename__ = "trigger_mail_settings"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    trigger_event: Mapped[str] = mapped_column(String(100), nullable=False)
    mail_campaign_id: Mapped[int] = mapped_column(Integer, ForeignKey("mail_campaigns.id"), nullable=False)
    delay_minutes: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, default=True, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
