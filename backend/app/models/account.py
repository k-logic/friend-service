import enum
from datetime import datetime

from sqlalchemy import String, Integer, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class AccountRole(str, enum.Enum):
    user = "user"
    staff = "staff"
    admin = "admin"


class AccountStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"


class Account(Base):
    __tablename__ = "accounts"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    credit_balance: Mapped[int] = mapped_column(Integer, default=0, nullable=False)
    role: Mapped[AccountRole] = mapped_column(Enum(AccountRole), default=AccountRole.user, nullable=False)
    status: Mapped[AccountStatus] = mapped_column(Enum(AccountStatus), default=AccountStatus.active, nullable=False)
    avatar_url: Mapped[str | None] = mapped_column(String(500), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
