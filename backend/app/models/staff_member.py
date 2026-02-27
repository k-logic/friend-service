import enum
from datetime import datetime

from sqlalchemy import String, Integer, Enum, DateTime, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class StaffRole(str, enum.Enum):
    staff = "staff"
    admin = "admin"


class StaffStatus(str, enum.Enum):
    active = "active"
    suspended = "suspended"


class StaffMember(Base):
    __tablename__ = "staff_members"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    email: Mapped[str] = mapped_column(String(255), unique=True, nullable=False, index=True)
    display_name: Mapped[str] = mapped_column(String(100), nullable=False)
    hashed_password: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[StaffRole] = mapped_column(Enum(StaffRole), default=StaffRole.staff, nullable=False)
    status: Mapped[StaffStatus] = mapped_column(Enum(StaffStatus), default=StaffStatus.active, nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now(), onupdate=func.now())
