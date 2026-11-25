import uuid
from datetime import datetime
from decimal import Decimal

from sqlalchemy import DateTime, Enum, ForeignKey, Numeric, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import WishlistCategory, WishlistPriority


class WishlistItem(Base):
    __tablename__ = "wishlists"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    participant_id: Mapped[str] = mapped_column(ForeignKey("group_participants.id"), nullable=False, index=True)
    title: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    product_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    image_url: Mapped[str | None] = mapped_column(String(1000), nullable=True)
    estimated_price: Mapped[Decimal | None] = mapped_column(Numeric(10, 2), nullable=True)
    priority: Mapped[WishlistPriority] = mapped_column(Enum(WishlistPriority), default=WishlistPriority.MEDIUM)
    category: Mapped[WishlistCategory] = mapped_column(Enum(WishlistCategory), default=WishlistCategory.OTHER)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="wishlist_items")
    participant = relationship("GroupParticipant", back_populates="wishlist_items")
