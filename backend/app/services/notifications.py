from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.models.enums import NotificationType
from app.models.group import Group
from app.models.notification import Notification
from app.models.participant import GroupParticipant
from app.models.user import User
from app.services.mailer import send_email


def create_notification(
    db: Session,
    *,
    user_id: str,
    title: str,
    message: str,
    notification_type: NotificationType,
    group_id: str | None = None,
    deep_link: str | None = None,
) -> Notification:
    item = Notification(
        user_id=user_id,
        group_id=group_id,
        notification_type=notification_type,
        title=title,
        message=message,
        deep_link=deep_link,
    )
    db.add(item)
    return item


def send_assignment_notice(
    db: Session,
    group: Group,
    giver: GroupParticipant,
    receiver: GroupParticipant,
    receiver_user: User,
    giver_user: User,
) -> None:
    title = "Your Secret Santa assignment is ready"
    in_app = (
        f"You are the Secret Santa for {receiver_user.full_name} in {group.name}. "
        "Open the assignment screen for budget, date, and wishlist details. Keep this private."
    )
    create_notification(
        db,
        user_id=giver_user.id,
        group_id=group.id,
        notification_type=NotificationType.ASSIGNMENT,
        title=title,
        message=in_app,
        deep_link=f"/groups/{group.id}/assignment",
    )
    email_body = f"""Hello {giver_user.full_name},

Congratulations! You are now the Secret Santa for {receiver_user.full_name}.

Here are some details:

- Recipient: {receiver_user.full_name}
- Gift budget: {group.currency} {group.minimum_budget}–{group.maximum_budget}
- Exchange date: {group.event_date.isoformat()}

Open the SecretSanta app to view {receiver_user.full_name}'s wishlist.

Keep your identity secret until the reveal!

This email is private. Do not forward it.
"""
    send_email(
        giver_user.email,
        "Your Secret Santa Assignment Is Ready!",
        email_body,
    )


def mark_read(notification: Notification) -> Notification:
    if notification.read_at is None:
        notification.read_at = datetime.now(timezone.utc)
    return notification
