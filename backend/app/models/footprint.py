from datetime import datetime

from sqlalchemy import Integer, DateTime, ForeignKey, Index, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column

from app.database import Base


class Footprint(Base):
    __tablename__ = "footprints"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, autoincrement=True)
    visitor_account_id: Mapped[int] = mapped_column(Integer, ForeignKey("accounts.id"), nullable=False, index=True)
    persona_id: Mapped[int] = mapped_column(Integer, ForeignKey("personas.id"), nullable=False)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    __table_args__ = (
        Index("ix_footprints_persona_created", "persona_id", "created_at"),
        UniqueConstraint("visitor_account_id", "persona_id", name="uq_footprints_visitor_persona"),
    )
