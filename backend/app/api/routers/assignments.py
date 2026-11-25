import threading
from datetime import datetime, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.models.group import Group

from app.api.deps import get_current_user, get_group, require_member, require_organizer
from app.database import get_db
from app.models.assignment import AssignmentExclusion, SecretSantaAssignment
from app.models.audit import AuditLog
from app.models.enums import AssignmentStatus, GiftStatus, GroupStatus, ParticipationStatus, PrivacyMode
from app.models.gift import GiftTracking
from app.models.participant import GroupParticipant
from app.models.user import User
from app.models.wishlist import WishlistItem
from app.schemas.common import AssignmentMeResponse, AssignmentRow, DrawResponse, WishlistPublic
from app.services.assignment import AssignmentImpossibleError, draw, validate_mapping
from app.services.notifications import send_assignment_notice

router = APIRouter(tags=["assignments"])
_draw_locks: dict[str, threading.Lock] = {}
_draw_locks_guard = threading.Lock()


def _group_lock(group_id: str) -> threading.Lock:
    with _draw_locks_guard:
        return _draw_locks.setdefault(group_id, threading.Lock())


def _lock_group_row(db: Session, group_id: str) -> Group:
    query = db.query(Group).filter(Group.id == group_id)
    try:
        return query.with_for_update().one()
    except Exception:
        return query.one()


def _joined_participants(db: Session, group_id: str) -> list[GroupParticipant]:
    return (
        db.query(GroupParticipant)
        .options(joinedload(GroupParticipant.user))
        .filter(
            GroupParticipant.group_id == group_id,
            GroupParticipant.participation_status == ParticipationStatus.JOINED,
        )
        .all()
    )


@router.post("/api/groups/{group_id}/assignments/draw", response_model=DrawResponse)
def run_draw(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> DrawResponse:
    group = get_group(group_id, db)
    require_organizer(group, current)

    lock = _group_lock(group.id)
    if not lock.acquire(blocking=False):
        raise HTTPException(status_code=409, detail="A draw is already running for this group")
    try:
        locked_group = _lock_group_row(db, group.id)
        if locked_group.assignment_status == AssignmentStatus.IN_PROGRESS:
            raise HTTPException(status_code=409, detail="A draw is already running for this group")
        if locked_group.assignment_status == AssignmentStatus.COMPLETED:
            raise HTTPException(
                status_code=409,
                detail="Assignments already exist. Reset them explicitly before drawing again.",
            )
        if locked_group.status == GroupStatus.CANCELLED:
            raise HTTPException(status_code=400, detail="This group has been cancelled")

        participants = _joined_participants(db, locked_group.id)
        if len(participants) < 2:
            raise HTTPException(status_code=400, detail="At least 2 participants are required to draw")

        locked_group.assignment_status = AssignmentStatus.IN_PROGRESS
        db.flush()

        exclusions_rows = db.query(AssignmentExclusion).filter(AssignmentExclusion.group_id == locked_group.id).all()
        exclusions: dict[str, set[str]] = {}
        for row in exclusions_rows:
            exclusions.setdefault(row.participant_id, set()).add(row.excluded_participant_id)

        ids = [p.id for p in participants]
        names = {p.id: (p.user.full_name if p.user else p.id) for p in participants}
        try:
            result = draw(ids, exclusions=exclusions, names=names)
            validate_mapping(result.mapping, ids)
        except AssignmentImpossibleError as exc:
            locked_group.assignment_status = AssignmentStatus.FAILED
            db.add(
                AuditLog(
                    group_id=locked_group.id,
                    actor_user_id=current.id,
                    action="assignment_failed",
                    details=" | ".join(exc.conflicts),
                )
            )
            db.commit()
            raise HTTPException(
                status_code=422,
                detail={"message": exc.message, "conflicts": exc.conflicts},
            ) from exc

        for giver_id, receiver_id in result.mapping.items():
            assignment = SecretSantaAssignment(
                group_id=locked_group.id,
                giver_participant_id=giver_id,
                receiver_participant_id=receiver_id,
                assigned_at=datetime.now(timezone.utc),
            )
            db.add(assignment)
            db.flush()
            db.add(
                GiftTracking(
                    group_id=locked_group.id,
                    assignment_id=assignment.id,
                    gift_status=GiftStatus.NOT_STARTED,
                )
            )

        people = {p.id: p for p in participants}
        for giver_id, receiver_id in result.mapping.items():
            giver = people[giver_id]
            receiver = people[receiver_id]
            if giver.user and receiver.user:
                send_assignment_notice(db, locked_group, giver, receiver, receiver.user, giver.user)

        locked_group.assignment_status = AssignmentStatus.COMPLETED
        locked_group.status = GroupStatus.DRAWN
        db.add(
            AuditLog(
                group_id=locked_group.id,
                actor_user_id=current.id,
                action="assignment_drawn",
                details=f"{len(result.mapping)} pairs",
            )
        )
        db.commit()
        return DrawResponse(
            assigned_count=len(result.mapping),
            message="Assignments created. Participants have been notified.",
        )
    finally:
        lock.release()


@router.get("/api/groups/{group_id}/assignments/me", response_model=AssignmentMeResponse)
def my_assignment(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> AssignmentMeResponse:
    group = get_group(group_id, db)
    member = require_member(group, current, db)
    assignment = (
        db.query(SecretSantaAssignment)
        .filter(
            SecretSantaAssignment.group_id == group.id,
            SecretSantaAssignment.giver_participant_id == member.id,
        )
        .one_or_none()
    )
    if assignment is None:
        raise HTTPException(status_code=404, detail="No assignment yet. Wait for the organizer to start the draw.")
    receiver = db.get(GroupParticipant, assignment.receiver_participant_id)
    receiver_user = receiver.user if receiver else None
    items = (
        db.query(WishlistItem)
        .filter(WishlistItem.group_id == group.id, WishlistItem.participant_id == assignment.receiver_participant_id)
        .all()
    )
    tracking = db.query(GiftTracking).filter(GiftTracking.assignment_id == assignment.id).one_or_none()
    return AssignmentMeResponse(
        assignment_id=assignment.id,
        group_id=group.id,
        receiver_participant_id=assignment.receiver_participant_id,
        receiver_name=receiver_user.full_name if receiver_user else "Recipient",
        receiver_country=receiver.country if receiver else None,
        receiver_preferences=receiver.gift_preferences if receiver else None,
        receiver_interests=receiver.interests if receiver else None,
        receiver_hobbies=receiver.hobbies if receiver else None,
        budget_min=group.minimum_budget,
        budget_max=group.maximum_budget,
        currency=group.currency,
        event_date=group.event_date,
        wishlist=[WishlistPublic.model_validate(item) for item in items],
        gift_status=tracking.gift_status if tracking else None,
    )


@router.get("/api/groups/{group_id}/assignments", response_model=list[AssignmentRow])
def list_assignments(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[AssignmentRow]:
    group = get_group(group_id, db)
    require_member(group, current, db)
    if group.privacy_mode == PrivacyMode.SECRET and group.organizer_id != current.id:
        raise HTTPException(status_code=403, detail="The full assignment list is private in Secret Santa mode")
    if group.privacy_mode == PrivacyMode.ORGANIZER and group.organizer_id != current.id:
        raise HTTPException(status_code=403, detail="Only the organizer can view every assignment")
    if group.privacy_mode == PrivacyMode.SECRET:
        raise HTTPException(status_code=403, detail="Organizer-hidden mode does not expose the mapping")

    rows = db.query(SecretSantaAssignment).filter(SecretSantaAssignment.group_id == group.id).all()
    people = {p.id: p for p in _joined_participants(db, group.id)}
    result = []
    for row in rows:
        giver = people.get(row.giver_participant_id)
        receiver = people.get(row.receiver_participant_id)
        result.append(
            AssignmentRow(
                giver_participant_id=row.giver_participant_id,
                giver_name=giver.user.full_name if giver and giver.user else "Member",
                receiver_participant_id=row.receiver_participant_id,
                receiver_name=receiver.user.full_name if receiver and receiver.user else "Member",
            )
        )
    return result


@router.post("/api/groups/{group_id}/assignments/reset", response_model=DrawResponse)
def reset_assignments(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> DrawResponse:
    group = get_group(group_id, db)
    require_organizer(group, current)
    locked = db.query(type(group)).filter_by(id=group.id).with_for_update().one()
    db.query(GiftTracking).filter(GiftTracking.group_id == locked.id).delete()
    deleted = db.query(SecretSantaAssignment).filter(SecretSantaAssignment.group_id == locked.id).delete()
    locked.assignment_status = AssignmentStatus.NOT_STARTED
    locked.status = GroupStatus.OPEN
    db.add(AuditLog(group_id=locked.id, actor_user_id=current.id, action="assignment_reset", details=str(deleted)))
    db.commit()
    return DrawResponse(assigned_count=0, message="Assignments cleared. You can draw again.")
