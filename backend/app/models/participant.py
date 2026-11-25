import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Enum, ForeignKey, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import ParticipantRole, ParticipationStatus


class GroupParticipant(Base):
    __tablename__ = "group_participants"
    __table_args__ = (UniqueConstraint("group_id", "user_id", name="uq_group_user"),)

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    user_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    role: Mapped[ParticipantRole] = mapped_column(Enum(ParticipantRole), default=ParticipantRole.PARTICIPANT)
    participation_status: Mapped[ParticipationStatus] = mapped_column(
        Enum(ParticipationStatus), default=ParticipationStatus.JOINED
    )
    wishlist_completed: Mapped[bool] = mapped_column(Boolean, default=False)
    gift_preferences: Mapped[str | None] = mapped_column(Text, nullable=True)
    interests: Mapped[str | None] = mapped_column(Text, nullable=True)
    hobbies: Mapped[str | None] = mapped_column(Text, nullable=True)
    budget_acknowledged: Mapped[bool] = mapped_column(Boolean, default=False)
    shipping_address: Mapped[str | None] = mapped_column(Text, nullable=True)
    country: Mapped[str | None] = mapped_column(String(80), nullable=True)
    organizer_wishlist_authorized: Mapped[bool] = mapped_column(Boolean, default=False)
    joined_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="participants")
    user = relationship("User", back_populates="participations")
    wishlist_items = relationship("WishlistItem", back_populates="participant", cascade="all, delete-orphan")
