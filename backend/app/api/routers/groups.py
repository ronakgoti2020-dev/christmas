from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session, joinedload

from app.api.deps import get_current_user, get_group, require_organizer
from app.config import get_settings
from app.database import get_db
from app.models.audit import AuditLog
from app.models.enums import GroupStatus, ParticipantRole, ParticipationStatus
from app.models.group import Group
from app.models.participant import GroupParticipant
from app.models.user import User
from app.models.invitation import GroupInvitation
from app.models.notification import Notification
from app.schemas.common import (
    DashboardResponse,
    GroupCreateRequest,
    GroupPublic,
    GroupUpdateRequest,
    MessageResponse,
    UserPublic,
)
from app.services.security import generate_invite_code, slugify

router = APIRouter(tags=["groups"])


def _invite_url(invite_code: str) -> str:
    return f"{get_settings().frontend_url}/join/{invite_code}"


def serialize_group(group: Group, participant_count: int | None = None) -> GroupPublic:
    data = GroupPublic.model_validate(group)
    data.invite_url = _invite_url(group.invite_code)
    data.assignment_status = group.assignment_status.value if hasattr(group.assignment_status, "value") else str(group.assignment_status)
    if participant_count is not None:
        data.participant_count = participant_count
    else:
        data.participant_count = len(
            [p for p in group.participants if p.participation_status == ParticipationStatus.JOINED]
        )
    return data


@router.post("/api/groups", response_model=GroupPublic, status_code=201)
def create_group(
    payload: GroupCreateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> GroupPublic:
    if payload.registration_deadline > payload.event_date:
        raise HTTPException(status_code=400, detail="Registration must close on or before the exchange date")
    invite_code = generate_invite_code(payload.name, payload.event_date.year)
    group = Group(
        name=payload.name.strip(),
        slug=invite_code,
        description=payload.description,
        event_type=payload.event_type,
        event_date=payload.event_date,
        registration_deadline=payload.registration_deadline,
        minimum_budget=payload.minimum_budget,
        maximum_budget=payload.maximum_budget,
        currency=payload.currency.upper(),
        country=payload.country,
        exchange_type=payload.exchange_type,
        privacy_mode=payload.privacy_mode,
        visibility=payload.visibility,
        organizer_id=current.id,
        invite_code=invite_code,
        reveal_identities=payload.reveal_identities,
        theme=payload.theme or ("christmas" if payload.event_type.value == "christmas" else "classic"),
        status=GroupStatus.OPEN,
    )
    db.add(group)
    db.flush()
    db.add(
        GroupParticipant(
            group_id=group.id,
            user_id=current.id,
            role=ParticipantRole.ORGANIZER,
            participation_status=ParticipationStatus.JOINED,
            country=current.country or payload.country,
            budget_acknowledged=True,
        )
    )
    db.add(AuditLog(group_id=group.id, actor_user_id=current.id, action="group_created", details=group.name))
    db.commit()
    db.refresh(group)
    return serialize_group(group, participant_count=1)


@router.get("/api/groups", response_model=list[GroupPublic])
def list_groups(db: Session = Depends(get_db), current: User = Depends(get_current_user)) -> list[GroupPublic]:
    rows = (
        db.query(Group)
        .options(joinedload(Group.participants))
        .join(GroupParticipant, GroupParticipant.group_id == Group.id)
        .filter(
            GroupParticipant.user_id == current.id,
            GroupParticipant.participation_status == ParticipationStatus.JOINED,
        )
        .order_by(Group.event_date.asc())
        .all()
    )
    return [serialize_group(group) for group in rows]


@router.get("/api/dashboard", response_model=DashboardResponse)
def dashboard(db: Session = Depends(get_db), current: User = Depends(get_current_user)) -> DashboardResponse:
    from datetime import date

    groups = (
        db.query(Group)
        .options(joinedload(Group.participants))
        .join(GroupParticipant)
        .filter(
            GroupParticipant.user_id == current.id,
            GroupParticipant.participation_status == ParticipationStatus.JOINED,
            Group.status.in_([GroupStatus.OPEN, GroupStatus.DRAWN, GroupStatus.REVEALED]),
        )
        .all()
    )
    upcoming = [g for g in groups if g.event_date >= date.today()]
    unread = (
        db.query(Notification)
        .filter(Notification.user_id == current.id, Notification.read_at.is_(None))
        .count()
    )
    pending = (
        db.query(GroupInvitation)
        .filter(GroupInvitation.invitation_email == current.email)
        .count()
    )
    return DashboardResponse(
        user=UserPublic.model_validate(current),
        active_groups=[serialize_group(g) for g in groups],
        upcoming_exchanges=[serialize_group(g) for g in upcoming],
        pending_invites=pending,
        unread_notifications=unread,
    )


@router.get("/api/groups/{group_id}", response_model=GroupPublic)
def get_group_detail(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> GroupPublic:
    group = get_group(group_id, db)
    from app.api.deps import require_member

    require_member(group, current, db)
    return serialize_group(group)


@router.patch("/api/groups/{group_id}", response_model=GroupPublic)
def update_group(
    group_id: str,
    payload: GroupUpdateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> GroupPublic:
    group = get_group(group_id, db)
    require_organizer(group, current)
    updates = payload.model_dump(exclude_unset=True)
    if "name" in updates and updates["name"]:
        group.slug = slugify(updates["name"]) + "-" + group.invite_code.split("-")[-1]
    for key, value in updates.items():
        setattr(group, key, value)
    db.add(AuditLog(group_id=group.id, actor_user_id=current.id, action="group_updated"))
    db.commit()
    db.refresh(group)
    return serialize_group(group)


@router.delete("/api/groups/{group_id}", response_model=MessageResponse)
def delete_group(
    group_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> MessageResponse:
    group = get_group(group_id, db)
    require_organizer(group, current)
    group.status = GroupStatus.CANCELLED
    db.add(AuditLog(group_id=group.id, actor_user_id=current.id, action="group_cancelled"))
    db.commit()
    return MessageResponse(message="Group cancelled")
