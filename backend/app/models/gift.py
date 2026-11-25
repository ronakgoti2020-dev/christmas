import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import GiftStatus


class GiftTracking(Base):
    __tablename__ = "gift_tracking"
    __table_args__ = (UniqueConstraint("assignment_id", name="uq_gift_assignment"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    assignment_id: Mapped[str] = mapped_column(ForeignKey("secret_santa_assignments.id"), nullable=False)
    gift_status: Mapped[GiftStatus] = mapped_column(Enum(GiftStatus), default=GiftStatus.NOT_STARTED)
    gift_description: Mapped[str | None] = mapped_column(Text, nullable=True)
    tracking_reference: Mapped[str | None] = mapped_column(String(120), nullable=True)
    photo_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    group = relationship("Group", back_populates="gift_trackings")
    assignment = relationship("SecretSantaAssignment", back_populates="gift_tracking")
