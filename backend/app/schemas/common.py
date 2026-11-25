from datetime import date, datetime
from decimal import Decimal

from pydantic import BaseModel, ConfigDict, EmailStr, Field, field_validator

from app.models.enums import (
    EventType,
    ExchangeType,
    GiftStatus,
    GroupStatus,
    GroupVisibility,
    PrivacyMode,
    WishlistCategory,
    WishlistPriority,
)


class ORMModel(BaseModel):
    model_config = ConfigDict(from_attributes=True)


class TokenResponse(BaseModel):
    access_token: str
    token_type: str = "bearer"
    user: "UserPublic"


class UserPublic(ORMModel):
    id: str
    full_name: str
    email: EmailStr
    profile_image: str | None
    country: str | None
    email_verified: bool


class RegisterRequest(BaseModel):
    full_name: str = Field(min_length=2, max_length=120)
    email: EmailStr
    password: str = Field(min_length=8, max_length=128)
    country: str | None = None

    @field_validator("password")
    @classmethod
    def strong_enough(cls, value: str) -> str:
        if value.lower() == value or value.upper() == value or not any(ch.isdigit() for ch in value):
            raise ValueError("Password must include mixed case and a number.")
        return value


class LoginRequest(BaseModel):
    email: EmailStr
    password: str


class GoogleAuthRequest(BaseModel):
    id_token: str


class ForgotPasswordRequest(BaseModel):
    email: EmailStr


class ResetPasswordRequest(BaseModel):
    token: str
    password: str = Field(min_length=8, max_length=128)


class VerifyEmailRequest(BaseModel):
    token: str


class ProfileUpdateRequest(BaseModel):
    full_name: str | None = Field(default=None, min_length=2, max_length=120)
    country: str | None = None
    profile_image: str | None = None


class GroupCreateRequest(BaseModel):
    name: str = Field(min_length=2, max_length=160)
    description: str | None = None
    event_type: EventType = EventType.CHRISTMAS
    event_date: date
    registration_deadline: date
    minimum_budget: Decimal = Field(gt=0)
    maximum_budget: Decimal = Field(gt=0)
    currency: str = Field(default="USD", min_length=3, max_length=8)
    country: str = Field(min_length=2, max_length=80)
    exchange_type: ExchangeType = ExchangeType.PHYSICAL
    privacy_mode: PrivacyMode = PrivacyMode.SECRET
    visibility: GroupVisibility = GroupVisibility.PRIVATE
    reveal_identities: bool = False
    theme: str = "christmas"

    @field_validator("maximum_budget")
    @classmethod
    def budget_range(cls, maximum: Decimal, info):
        minimum = info.data.get("minimum_budget")
        if minimum is not None and maximum < minimum:
            raise ValueError("Maximum budget must be greater than or equal to minimum budget.")
        return maximum


class GroupUpdateRequest(BaseModel):
    name: str | None = Field(default=None, min_length=2, max_length=160)
    description: str | None = None
    event_date: date | None = None
    registration_deadline: date | None = None
    minimum_budget: Decimal | None = None
    maximum_budget: Decimal | None = None
    currency: str | None = None
    country: str | None = None
    exchange_type: ExchangeType | None = None
    privacy_mode: PrivacyMode | None = None
    visibility: GroupVisibility | None = None
    reveal_identities: bool | None = None
    status: GroupStatus | None = None
    theme: str | None = None


class GroupPublic(ORMModel):
    id: str
    name: str
    slug: str
    description: str | None
    event_type: EventType
    event_date: date
    registration_deadline: date
    minimum_budget: Decimal
    maximum_budget: Decimal
    currency: str
    country: str
    exchange_type: ExchangeType
    privacy_mode: PrivacyMode
    visibility: GroupVisibility
    organizer_id: str
    invite_code: str
    invite_url: str | None = None
    status: GroupStatus
    assignment_status: str
    reveal_identities: bool
    theme: str
    participant_count: int = 0
    created_at: datetime


class JoinPreview(BaseModel):
    name: str
    description: str | None
    event_type: EventType
    event_date: date
    registration_deadline: date
    minimum_budget: Decimal
    maximum_budget: Decimal
    currency: str
    country: str
    exchange_type: ExchangeType
    organizer_name: str
    already_joined: bool = False
    closed: bool = False


class JoinRequest(BaseModel):
    gift_preferences: str | None = None
    interests: str | None = None
    hobbies: str | None = None
    budget_acknowledged: bool = True
    shipping_address: str | None = None
    country: str | None = None
    full_name: str | None = None
    email: EmailStr | None = None
    password: str | None = None


class InvitationCreateRequest(BaseModel):
    email: EmailStr | None = None
    expires_in_days: int = Field(default=21, ge=1, le=120)


class InvitationPublic(ORMModel):
    id: str
    invitation_email: str | None
    invitation_code: str
    status: str
    expires_at: datetime | None
    created_at: datetime
    invite_url: str | None = None


class ParticipantPublic(ORMModel):
    id: str
    user_id: str
    full_name: str
    email: str | None = None
    profile_image: str | None
    country: str | None
    role: str
    participation_status: str
    wishlist_completed: bool
    has_assignment: bool = False
    joined_at: datetime
    gift_preferences: str | None = None
    interests: str | None = None
    hobbies: str | None = None
    access_token: str | None = None


class ExclusionCreateRequest(BaseModel):
    participant_id: str
    excluded_participant_id: str
    reason: str | None = None


class WishlistCreateRequest(BaseModel):
    title: str = Field(min_length=1, max_length=200)
    description: str | None = None
    product_url: str | None = None
    image_url: str | None = None
    estimated_price: Decimal | None = None
    priority: WishlistPriority = WishlistPriority.MEDIUM
    category: WishlistCategory = WishlistCategory.OTHER


class WishlistUpdateRequest(BaseModel):
    title: str | None = None
    description: str | None = None
    product_url: str | None = None
    image_url: str | None = None
    estimated_price: Decimal | None = None
    priority: WishlistPriority | None = None
    category: WishlistCategory | None = None
    organizer_wishlist_authorized: bool | None = None


class WishlistPublic(ORMModel):
    id: str
    group_id: str
    participant_id: str
    title: str
    description: str | None
    product_url: str | None
    image_url: str | None
    estimated_price: Decimal | None
    priority: WishlistPriority
    category: WishlistCategory
    created_at: datetime


class AssignmentMeResponse(BaseModel):
    assignment_id: str
    group_id: str
    receiver_participant_id: str
    receiver_name: str
    receiver_country: str | None
    receiver_preferences: str | None
    receiver_interests: str | None
    receiver_hobbies: str | None
    budget_min: Decimal
    budget_max: Decimal
    currency: str
    event_date: date
    wishlist: list[WishlistPublic]
    gift_status: GiftStatus | None = None


class AssignmentRow(BaseModel):
    giver_participant_id: str
    giver_name: str
    receiver_participant_id: str
    receiver_name: str


class DrawResponse(BaseModel):
    assigned_count: int
    message: str


class DrawErrorResponse(BaseModel):
    detail: str
    conflicts: list[str]


class GiftStatusUpdateRequest(BaseModel):
    gift_status: GiftStatus
    gift_description: str | None = None
    tracking_reference: str | None = None
    photo_url: str | None = None


class GiftProgressPublic(BaseModel):
    participant_id: str
    full_name: str
    gift_status: GiftStatus
    updated_at: datetime | None = None


class NotificationPublic(ORMModel):
    id: str
    group_id: str | None
    notification_type: str
    title: str
    message: str
    deep_link: str | None
    read_at: datetime | None
    created_at: datetime


class DashboardResponse(BaseModel):
    user: UserPublic
    active_groups: list[GroupPublic]
    upcoming_exchanges: list[GroupPublic]
    pending_invites: int
    unread_notifications: int


class MessageResponse(BaseModel):
    message: str


class RevealMessageCreateRequest(BaseModel):
    body: str = Field(min_length=1, max_length=1000)


class RevealMessagePublic(ORMModel):
    id: str
    author_name: str
    body: str
    created_at: datetime
