from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.api.deps import get_current_user
from app.database import get_db
from app.models.notification import Notification
from app.models.user import User
from app.schemas.common import NotificationPublic
from app.services.notifications import mark_read

router = APIRouter(tags=["notifications"])


@router.get("/api/notifications", response_model=list[NotificationPublic])
def list_notifications(
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> list[NotificationPublic]:
    rows = (
        db.query(Notification)
        .filter(Notification.user_id == current.id)
        .order_by(Notification.created_at.desc())
        .limit(100)
        .all()
    )
    return [NotificationPublic.model_validate(row) for row in rows]


@router.patch("/api/notifications/{notification_id}/read", response_model=NotificationPublic)
def read_notification(
    notification_id: str,
    db: Session = Depends(get_db),
    current: User = Depends(get_current_user),
) -> NotificationPublic:
    item = db.get(Notification, notification_id)
    if item is None or item.user_id != current.id:
        raise HTTPException(status_code=404, detail="Notification not found")
    mark_read(item)
    db.commit()
    db.refresh(item)
    return NotificationPublic.model_validate(item)
