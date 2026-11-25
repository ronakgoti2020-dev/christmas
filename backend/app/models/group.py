import uuid
from datetime import date, datetime
from decimal import Decimal

from sqlalchemy import Boolean, Date, DateTime, Enum, ForeignKey, Numeric, String, Text, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import (
    AssignmentStatus,
    EventType,
    ExchangeType,
    GroupStatus,
    GroupVisibility,
    PrivacyMode,
)


class Group(Base):
    __tablename__ = "groups"
    __table_args__ = (
        UniqueConstraint("slug", name="uq_groups_slug"),
        UniqueConstraint("invite_code", name="uq_groups_invite_code"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name: Mapped[str] = mapped_column(String(160), nullable=False)
    slug: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    event_type: Mapped[EventType] = mapped_column(Enum(EventType), default=EventType.CHRISTMAS)
    event_date: Mapped[date] = mapped_column(Date, nullable=False)
    registration_deadline: Mapped[date] = mapped_column(Date, nullable=False)
    minimum_budget: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    maximum_budget: Mapped[Decimal] = mapped_column(Numeric(10, 2), nullable=False)
    currency: Mapped[str] = mapped_column(String(8), default="USD")
    country: Mapped[str] = mapped_column(String(80), nullable=False)
    exchange_type: Mapped[ExchangeType] = mapped_column(Enum(ExchangeType), default=ExchangeType.PHYSICAL)
    privacy_mode: Mapped[PrivacyMode] = mapped_column(Enum(PrivacyMode), default=PrivacyMode.SECRET)
    visibility: Mapped[GroupVisibility] = mapped_column(Enum(GroupVisibility), default=GroupVisibility.PRIVATE)
    organizer_id: Mapped[str] = mapped_column(ForeignKey("users.id"), nullable=False, index=True)
    invite_code: Mapped[str] = mapped_column(String(180), nullable=False, index=True)
    status: Mapped[GroupStatus] = mapped_column(Enum(GroupStatus), default=GroupStatus.OPEN)
    assignment_status: Mapped[AssignmentStatus] = mapped_column(
        Enum(AssignmentStatus), default=AssignmentStatus.NOT_STARTED
    )
    reveal_identities: Mapped[bool] = mapped_column(Boolean, default=False)
    theme: Mapped[str] = mapped_column(String(40), default="christmas")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now(), onupdate=func.now()
    )

    organizer = relationship("User", back_populates="organized_groups")
    participants = relationship("GroupParticipant", back_populates="group", cascade="all, delete-orphan")
    wishlist_items = relationship("WishlistItem", back_populates="group", cascade="all, delete-orphan")
    exclusions = relationship("AssignmentExclusion", back_populates="group", cascade="all, delete-orphan")
    assignments = relationship("SecretSantaAssignment", back_populates="group", cascade="all, delete-orphan")
    invitations = relationship("GroupInvitation", back_populates="group", cascade="all, delete-orphan")
    gift_trackings = relationship("GiftTracking", back_populates="group", cascade="all, delete-orphan")
    notifications = relationship("Notification", back_populates="group")
