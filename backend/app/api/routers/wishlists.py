from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.api.deps import get_current_user, get_group, require_member
from app.database import get_db
from app.models.assignment import SecretSantaAssignment
from app.models.enums import PrivacyMode
from app.models.participant import GroupParticipant
from app.models.user import User
from app.models.wishlist import WishlistItem
from app.schemas.common import WishlistCreateRequest, WishlistPublic, WishlistUpdateRequest

router = APIRouter(tags=["wishlists"])


def _can_view_wishlist(
    *,
    group,
    viewer: GroupParticipant,
    owner: GroupParticipant,
    db: Session,
    user: User,
) -> bool:
    if owner.id == viewer.id:
        return True
    if owner.organizer_wishlist_authorized and group.organizer_id == user.id:
        return True
    assignment = (
        db.query(SecretSantaAssignment)
        .filter(
            SecretSantaAssignment.group_id == group.id,
            SecretSantaAssignment.giver_participant_id == viewer.id,
            SecretSantaAssignment.receiver_participant_id == owner.id,
        )
        .one_or_none()
    )
    if assignment:
        return True
    if group.privacy_mode == PrivacyMode.PUBLIC:
        return True
    return False


@router.post("/api/groups/{group_id}/wishlist", response_model=WishlistPublic, status_code=201)
def add_item(
    group_id: str,
    payload: WishlistCreateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> WishlistPublic:
    group = get_group(group_id, db)
    member = require_member(group, current, db)
    item = WishlistItem(group_id=group.id, participant_id=member.id, **payload.model_dump())
    db.add(item)
    member.wishlist_completed = True
    db.commit()
    db.refresh(item)
    return WishlistPublic.model_validate(item)


@router.get("/api/groups/{group_id}/wishlist", response_model=list[WishlistPublic])
def list_wishlist(
    group_id: str,
    participant_id: str | None = None,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[WishlistPublic]:
    group = get_group(group_id, db)
    viewer = require_member(group, current, db)
    owner_id = participant_id or viewer.id
    owner = db.get(GroupParticipant, owner_id)
    if owner is None or owner.group_id != group.id:
        raise HTTPException(status_code=404, detail="Participant not found")
    if not _can_view_wishlist(group=group, viewer=viewer, owner=owner, db=db, user=current):
        raise HTTPException(status_code=403, detail="This wishlist is private")
    items = (
        db.query(WishlistItem)
        .filter(WishlistItem.group_id == group.id, WishlistItem.participant_id == owner.id)
        .order_by(WishlistItem.created_at.desc())
        .all()
    )
    return [WishlistPublic.model_validate(item) for item in items]


@router.patch("/api/groups/{group_id}/wishlist/{wishlist_id}", response_model=WishlistPublic)
def update_item(
    group_id: str,
    wishlist_id: str,
    payload: WishlistUpdateRequest,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> WishlistPublic:
    group = get_group(group_id, db)
    member = require_member(group, current, db)
    if payload.organizer_wishlist_authorized is not None:
        member.organizer_wishlist_authorized = payload.organizer_wishlist_authorized
        db.commit()
    item = db.get(WishlistItem, wishlist_id)
    if item is None or item.group_id != group.id:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    if item.participant_id != member.id:
        raise HTTPException(status_code=403, detail="You can only edit your own wishlist")
    for key, value in payload.model_dump(exclude_unset=True, exclude={"organizer_wishlist_authorized"}).items():
        setattr(item, key, value)
    db.commit()
    db.refresh(item)
    return WishlistPublic.model_validate(item)


@router.delete("/api/groups/{group_id}/wishlist/{wishlist_id}", status_code=204)
def delete_item(
    group_id: str,
    wishlist_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> None:
    group = get_group(group_id, db)
    member = require_member(group, current, db)
    item = db.get(WishlistItem, wishlist_id)
    if item is None or item.group_id != group.id:
        raise HTTPException(status_code=404, detail="Wishlist item not found")
    if item.participant_id != member.id:
        raise HTTPException(status_code=403, detail="You can only delete your own wishlist items")
    db.delete(item)
    remaining = (
        db.query(WishlistItem)
        .filter(WishlistItem.participant_id == member.id, WishlistItem.group_id == group.id)
        .count()
    )
    member.wishlist_completed = remaining > 1
    db.commit()
