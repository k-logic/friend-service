from datetime import datetime

from sqlalchemy import Integer, String, Text, Boolean, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class LineBotAccount(Base):
    __tablename__ = "line_bot_accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    line_bot_id: Mapped[str] = mapped_column(String(100), unique=True, nullable=False)
    memo: Mapped[str | None] = mapped_column(Text, nullable=True)
    webhook_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, default=False, nullable=False)
    subscriber_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    monthly_delivery_count: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
