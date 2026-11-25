import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, String, UniqueConstraint, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base


class AssignmentExclusion(Base):
    __tablename__ = "assignment_exclusions"
    __table_args__ = (
        UniqueConstraint("group_id", "participant_id", "excluded_participant_id", name="uq_exclusion_pair"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    participant_id: Mapped[str] = mapped_column(ForeignKey("group_participants.id"), nullable=False)
    excluded_participant_id: Mapped[str] = mapped_column(ForeignKey("group_participants.id"), nullable=False)
    reason: Mapped[str | None] = mapped_column(String(255), nullable=True)

    group = relationship("Group", back_populates="exclusions")
    participant = relationship("GroupParticipant", foreign_keys=[participant_id])
    excluded_participant = relationship("GroupParticipant", foreign_keys=[excluded_participant_id])


class SecretSantaAssignment(Base):
    __tablename__ = "secret_santa_assignments"
    __table_args__ = (
        UniqueConstraint("group_id", "giver_participant_id", name="uq_assignment_giver"),
        UniqueConstraint("group_id", "receiver_participant_id", name="uq_assignment_receiver"),
    )

    id: Mapped[str] = mapped_column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id: Mapped[str] = mapped_column(ForeignKey("groups.id"), nullable=False, index=True)
    giver_participant_id: Mapped[str] = mapped_column(ForeignKey("group_participants.id"), nullable=False)
    receiver_participant_id: Mapped[str] = mapped_column(ForeignKey("group_participants.id"), nullable=False)
    assigned_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), server_default=func.now())

    group = relationship("Group", back_populates="assignments")
    giver = relationship("GroupParticipant", foreign_keys=[giver_participant_id])
    receiver = relationship("GroupParticipant", foreign_keys=[receiver_participant_id])
    gift_tracking = relationship("GiftTracking", back_populates="assignment", uselist=False)
