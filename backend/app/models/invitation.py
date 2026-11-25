import uuid
from datetime import datetime

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base
from app.models.enums import InvitationStatus


class GroupInvitation(Base):
    __tablename__ = "group_invitations"

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    invitation_email: Mapped[str | None] = mapped_column(String(255), nullable=True, index=True)
    invitation_code: Mapped[str] = mapped_column(String(180), unique=True, index=True, nullable=False)
    status: Mapped[InvitationStatus] = mapped_column(Enum(InvitationStatus), default=InvitationStatus.PENDING)
    expires_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="invitations")
