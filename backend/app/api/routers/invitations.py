from datetime import datetime, timedelta, timezone

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_group, get_optional_user, require_organizer
from app.config import get_settings
from app.database import get_db
from app.models.enums import GroupStatus, InvitationStatus, ParticipantRole, ParticipationStatus
from app.models.group import Group
from app.models.invitation import GroupInvitation
from app.models.participant import GroupParticipant
from app.models.user import User
from app.schemas.common import (
    InvitationCreateRequest,
    InvitationPublic,
    JoinPreview,
    JoinRequest,
    ParticipantPublic,
)
from app.services.mailer import send_email
from app.services.security import create_access_token, generate_invite_code, hash_password

router = APIRouter(tags=["invitations"])


def _url(code: str) -> str:
    return f"{get_settings().frontend_url}/join/{code}"


@router.post("/api/groups/{group_id}/invitations", response_model=InvitationPublic, status_code=201)
def create_invitation(
    group_id: str,
    payload: InvitationCreateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> InvitationPublic:
    group = get_group(group_id, db)
    require_organizer(group, current)
    code = generate_invite_code(group.name, group.event_date.year)
    invitation = GroupInvitation(
        group_id=group.id,
        invitation_email=payload.email.lower() if payload.email else None,
        invitation_code=code,
        status=InvitationStatus.PENDING,
        expires_at=datetime.now(timezone.utc) + timedelta(days=payload.expires_in_days),
    )
    db.add(invitation)
    db.commit()
    db.refresh(invitation)
    if payload.email:
        send_email(
            payload.email,
            f"You're invited to {group.name}",
            f"Join this Secret Santa group:\n{_url(group.invite_code)}\n\nGift budget: {group.currency} {group.minimum_budget}-{group.maximum_budget}",
        )
    data = InvitationPublic.model_validate(invitation)
    data.invite_url = _url(group.invite_code)
    return data


@router.get("/api/invitations/{invite_code}", response_model=JoinPreview)
def preview_invite(
    invite_code: str,
    db: Session = Depends(get_db),
    current: User | None = Depends(get_optional_user),
) -> JoinPreview:
    group = (
        db.query(Group)
        .options(joinedload(Group.organizer), joinedload(Group.participants))
        .filter(Group.invite_code == invite_code)
        .one_or_none()
    )
    if group is None:
        invitation = db.query(GroupInvitation).filter(GroupInvitation.invitation_code == invite_code).one_or_none()
        if invitation is None:
            raise HTTPException(status_code=404, detail="Invitation not found")
        if invitation.expires_at and invitation.expires_at < datetime.now(timezone.utc):
            raise HTTPException(status_code=410, detail="This invitation has expired")
        group = get_group(invitation.group_id, db)
    already = False
    if current:
        already = any(p.user_id == current.id and p.participation_status == ParticipationStatus.JOINED for p in group.participants)
    return JoinPreview(
        name=group.name,
        description=group.description,
        event_type=group.event_type,
        event_date=group.event_date,
        registration_deadline=group.registration_deadline,
        minimum_budget=group.minimum_budget,
        maximum_budget=group.maximum_budget,
        currency=group.currency,
        country=group.country,
        exchange_type=group.exchange_type,
        organizer_name=group.organizer.full_name if group.organizer else "Organizer",
        already_joined=already,
        closed=group.status != GroupStatus.OPEN or group.registration_deadline < datetime.now(timezone.utc).date(),
    )


@router.post("/api/invitations/{invite_code}/join", response_model=ParticipantPublic, status_code=201)
def join_group(
    invite_code: str,
    payload: JoinRequest,
    db: Session = Depends(get_db),
    current: User | None = Depends(get_optional_user),
) -> ParticipantPublic:
    from app.models.group import Group

    group = db.query(Group).options(joinedload(Group.participants)).filter(Group.invite_code == invite_code).one_or_none()
    if group is None:
        invitation = db.query(GroupInvitation).filter(GroupInvitation.invitation_code == invite_code).one_or_none()
        if invitation is None:
            raise HTTPException(status_code=404, detail="Invitation not found")
        group = get_group(invitation.group_id, db)
        if invitation.status != InvitationStatus.PENDING:
            raise HTTPException(status_code=400, detail="This invitation is no longer valid")
        invitation.status = InvitationStatus.ACCEPTED

    if group.status != GroupStatus.OPEN:
        raise HTTPException(status_code=400, detail="This group is not accepting new participants")
    if group.registration_deadline < datetime.now(timezone.utc).date():
        raise HTTPException(status_code=400, detail="Registration for this group has closed")
    if not payload.budget_acknowledged:
        raise HTTPException(status_code=400, detail="Please acknowledge the gift budget before joining")

    user = current
    if user is None:
        if not payload.email or not payload.password or not payload.full_name:
            raise HTTPException(status_code=400, detail="Create an account with name, email and password to join")
        existing = db.query(User).filter(User.email == payload.email.lower()).one_or_none()
        if existing:
            raise HTTPException(status_code=409, detail="An account with this email already exists. Sign in, then join.")
        user = User(
            full_name=payload.full_name.strip(),
            email=payload.email.lower(),
            password_hash=hash_password(payload.password),
            country=payload.country,
            email_verified=False,
        )
        db.add(user)
        db.flush()

    duplicate = (
        db.query(GroupParticipant)
        .filter(GroupParticipant.group_id == group.id, GroupParticipant.user_id == user.id)
        .one_or_none()
    )
    if duplicate and duplicate.participation_status == ParticipationStatus.JOINED:
        raise HTTPException(status_code=409, detail="You are already in this group")
    if duplicate:
        duplicate.participation_status = ParticipationStatus.JOINED
        participant = duplicate
    else:
        participant = GroupParticipant(
            group_id=group.id,
            user_id=user.id,
            role=ParticipantRole.PARTICIPANT,
            participation_status=ParticipationStatus.JOINED,
            gift_preferences=payload.gift_preferences,
            interests=payload.interests,
            hobbies=payload.hobbies,
            budget_acknowledged=True,
            shipping_address=payload.shipping_address,
            country=payload.country or user.country,
        )
        db.add(participant)
        db.flush()
    db.commit()
    db.refresh(participant)
    return ParticipantPublic(
        id=participant.id,
        user_id=user.id,
        full_name=user.full_name,
        email=user.email,
        profile_image=user.profile_image,
        country=participant.country,
        role=participant.role.value,
        participation_status=participant.participation_status.value,
        wishlist_completed=participant.wishlist_completed,
        joined_at=participant.joined_at,
        gift_preferences=participant.gift_preferences,
        interests=participant.interests,
        hobbies=participant.hobbies,
        access_token=None if current else create_access_token(user.id),
    )
