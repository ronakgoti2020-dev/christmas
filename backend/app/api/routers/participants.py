from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_group, require_member, require_organizer
from app.database import get_db
from app.models.assignment import AssignmentExclusion, SecretSantaAssignment
from app.models.enums import ParticipationStatus, PrivacyMode
from app.models.participant import GroupParticipant
from app.models.user import User
from app.schemas.common import ExclusionCreateRequest, MessageResponse, ParticipantPublic

router = APIRouter(tags=["participants"])


def _to_public(participant: GroupParticipant, include_email: bool, has_assignment: bool) -> ParticipantPublic:
    user = participant.user
    return ParticipantPublic(
        id=participant.id,
        user_id=participant.user_id,
        full_name=user.full_name if user else "Member",
        email=user.email if include_email and user else None,
        profile_image=user.profile_image if user else None,
        country=participant.country,
        role=participant.role.value,
        participation_status=participant.participation_status.value,
        wishlist_completed=participant.wishlist_completed,
        has_assignment=has_assignment,
        joined_at=participant.joined_at,
        gift_preferences=participant.gift_preferences,
        interests=participant.interests,
        hobbies=participant.hobbies,
    )


@router.get("/api/groups/{group_id}/participants", response_model=list[ParticipantPublic])
def list_participants(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[ParticipantPublic]:
    group = get_group(group_id, db)
    require_member(group, current, db)
    rows = (
        db.query(GroupParticipant)
        .options(joinedload(GroupParticipant.user))
        .filter(
            GroupParticipant.group_id == group.id,
            GroupParticipant.participation_status == ParticipationStatus.JOINED,
        )
        .all()
    )
    assigned_givers = {
        a.giver_participant_id
        for a in db.query(SecretSantaAssignment).filter(SecretSantaAssignment.group_id == group.id).all()
    }
    include_email = group.organizer_id == current.id
    return [_to_public(row, include_email, row.id in assigned_givers) for row in rows]


@router.delete("/api/groups/{group_id}/participants/{participant_id}", response_model=MessageResponse)
def remove_participant(
    group_id: str,
    participant_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> MessageResponse:
    group = get_group(group_id, db)
    require_organizer(group, current)
    participant = db.get(GroupParticipant, participant_id)
    if participant is None or participant.group_id != group.id:
        raise HTTPException(status_code=404, detail="Participant not found")
    if participant.user_id == group.organizer_id:
        raise HTTPException(status_code=400, detail="The organizer cannot be removed")
    if group.assignment_status.value == "completed":
        raise HTTPException(status_code=400, detail="Reset assignments before removing participants")
    participant.participation_status = ParticipationStatus.REMOVED
    db.commit()
    return MessageResponse(message="Participant removed")


@router.post("/api/groups/{group_id}/exclusions", status_code=201)
def add_exclusion(
    group_id: str,
    payload: ExclusionCreateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    group = get_group(group_id, db)
    member = require_member(group, current, db)
    if group.organizer_id != current.id and payload.participant_id != member.id:
        raise HTTPException(status_code=403, detail="You can only set exclusions for yourself")
    if payload.participant_id == payload.excluded_participant_id:
        raise HTTPException(status_code=400, detail="A person cannot exclude themselves")
    existing = (
        db.query(AssignmentExclusion)
        .filter(
            AssignmentExclusion.group_id == group.id,
            AssignmentExclusion.participant_id == payload.participant_id,
            AssignmentExclusion.excluded_participant_id == payload.excluded_participant_id,
        )
        .one_or_none()
    )
    if existing:
        return {"id": existing.id}
    row = AssignmentExclusion(
        group_id=group.id,
        participant_id=payload.participant_id,
        excluded_participant_id=payload.excluded_participant_id,
        reason=payload.reason,
    )
    db.add(row)
    db.commit()
    db.refresh(row)
    return {"id": row.id, "reason": row.reason}


@router.get("/api/groups/{group_id}/exclusions")
def list_exclusions(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    group = get_group(group_id, db)
    member = require_member(group, current, db)
    query = db.query(AssignmentExclusion).filter(AssignmentExclusion.group_id == group.id)
    if group.organizer_id != current.id:
        query = query.filter(AssignmentExclusion.participant_id == member.id)
    return [
        {
            "id": row.id,
            "participant_id": row.participant_id,
            "excluded_participant_id": row.excluded_participant_id,
            "reason": row.reason,
        }
        for row in query.all()
    ]
