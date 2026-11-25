from datetime import date

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_group, require_member, require_organizer
from app.database import get_db
from app.models.assignment import SecretSantaAssignment
from app.models.enums import GiftStatus, ParticipationStatus, PrivacyMode
from app.models.gift import GiftTracking
from app.models.message import GroupMessage
from app.models.participant import GroupParticipant
from app.models.user import User
from app.schemas.common import (
    GiftProgressPublic,
    GiftStatusUpdateRequest,
    MessageResponse,
    RevealMessageCreateRequest,
    RevealMessagePublic,
)

router = APIRouter(tags=["gifts"])


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


@router.patch("/api/groups/{group_id}/gift-status", response_model=MessageResponse)
def update_gift_status(
    group_id: str,
    payload: GiftStatusUpdateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> MessageResponse:
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
        raise HTTPException(status_code=404, detail="No assignment found")
    tracking = db.query(GiftTracking).filter(GiftTracking.assignment_id == assignment.id).one_or_none()
    if tracking is None:
        tracking = GiftTracking(group_id=group.id, assignment_id=assignment.id)
        db.add(tracking)
    tracking.gift_status = payload.gift_status
    if payload.gift_description is not None:
        tracking.gift_description = payload.gift_description
    if payload.tracking_reference is not None:
        tracking.tracking_reference = payload.tracking_reference
    if payload.photo_url is not None:
        tracking.photo_url = payload.photo_url
    db.commit()
    return MessageResponse(message="Gift status updated")


@router.get("/api/groups/{group_id}/gift-tracking", response_model=list[GiftProgressPublic])
def gift_progress(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[GiftProgressPublic]:
    group = get_group(group_id, db)
    member = require_member(group, current, db)
    rows = (
        db.query(GiftTracking)
        .options(joinedload(GiftTracking.assignment))
        .filter(GiftTracking.group_id == group.id)
        .all()
    )
    people = {p.id: p for p in _joined_participants(db, group.id)}
    progress = []
    for row in rows:
        assignment = row.assignment
        if assignment is None:
            continue
        giver = people.get(assignment.giver_participant_id)
        if group.organizer_id != current.id and assignment.giver_participant_id != member.id:
            progress.append(
                GiftProgressPublic(
                    participant_id=assignment.giver_participant_id,
                    full_name=giver.user.full_name if giver and giver.user else "Member",
                    gift_status=row.gift_status,
                )
            )
            continue
        progress.append(
            GiftProgressPublic(
                participant_id=assignment.giver_participant_id,
                full_name=giver.user.full_name if giver and giver.user else "You",
                gift_status=row.gift_status,
                updated_at=row.updated_at,
            )
        )
    if group.organizer_id != current.id:
        for item in progress:
            if item.participant_id != member.id:
                item.full_name = "Participant"
    return progress


@router.get("/api/groups/{group_id}/reveal")
def reveal_state(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
):
    group = get_group(group_id, db)
    require_member(group, current, db)
    today = date.today()
    unlocked = today >= group.event_date
    identities = []
    if unlocked and group.reveal_identities and group.privacy_mode != PrivacyMode.SECRET:
        assignments = db.query(SecretSantaAssignment).filter(SecretSantaAssignment.group_id == group.id).all()
        people = {p.id: p for p in group.participants}
        identities = [
            {
                "giver": people[a.giver_participant_id].user.full_name
                if people.get(a.giver_participant_id) and people[a.giver_participant_id].user
                else "Member",
                "receiver": people[a.receiver_participant_id].user.full_name
                if people.get(a.receiver_participant_id) and people[a.receiver_participant_id].user
                else "Member",
            }
            for a in assignments
        ]
    elif unlocked and group.reveal_identities:
        member = require_member(group, current, db)
        assignment = (
            db.query(SecretSantaAssignment)
            .filter(
                SecretSantaAssignment.group_id == group.id,
                SecretSantaAssignment.receiver_participant_id == member.id,
            )
            .one_or_none()
        )
        if assignment:
            giver = db.get(type(member), assignment.giver_participant_id)
            identities = [
                {
                    "giver": giver.user.full_name if giver and giver.user else "Your Secret Santa",
                    "receiver": current.full_name,
                }
            ]
    messages = (
        db.query(GroupMessage)
        .options(joinedload(GroupMessage.author))
        .filter(GroupMessage.group_id == group.id)
        .order_by(GroupMessage.created_at.asc())
        .all()
    )
    return {
        "event_date": group.event_date.isoformat(),
        "unlocked": unlocked,
        "reveal_identities": group.reveal_identities,
        "identities": identities if unlocked else [],
        "messages": [
            RevealMessagePublic(
                id=m.id,
                author_name=m.author.full_name if m.author else "Member",
                body=m.body,
                created_at=m.created_at,
            )
            for m in messages
        ],
    }


@router.post("/api/groups/{group_id}/reveal/messages", response_model=RevealMessagePublic, status_code=201)
def post_reveal_message(
    group_id: str,
    payload: RevealMessageCreateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> RevealMessagePublic:
    group = get_group(group_id, db)
    require_member(group, current, db)
    message = GroupMessage(group_id=group.id, author_user_id=current.id, body=payload.body.strip())
    db.add(message)
    db.commit()
    db.refresh(message)
    return RevealMessagePublic(
        id=message.id, author_name=current.full_name, body=message.body, created_at=message.created_at
    )
