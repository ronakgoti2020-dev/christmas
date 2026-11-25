import enum


class EventType(str, enum.Enum):
    CHRISTMAS = "christmas"
    BIRTHDAY = "birthday"
    OFFICE = "office"
    FAMILY = "family"
    FRIENDS = "friends"
    NEW_YEAR = "new_year"
    CUSTOM = "custom"


class ExchangeType(str, enum.Enum):
    PHYSICAL = "physical"
    DIGITAL = "digital"
    BOTH = "both"


class PrivacyMode(str, enum.Enum):
    SECRET = "secret"
    ORGANIZER = "organizer"
    PUBLIC = "public"


class GroupVisibility(str, enum.Enum):
    PRIVATE = "private"
    UNLISTED = "unlisted"
    PUBLIC = "public"


class GroupStatus(str, enum.Enum):
    DRAFT = "draft"
    OPEN = "open"
    CLOSED = "closed"
    DRAWN = "drawn"
    REVEALED = "revealed"
    COMPLETED = "completed"
    CANCELLED = "cancelled"


class AssignmentStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    FAILED = "failed"


class ParticipantRole(str, enum.Enum):
    ORGANIZER = "organizer"
    PARTICIPANT = "participant"


class ParticipationStatus(str, enum.Enum):
    INVITED = "invited"
    JOINED = "joined"
    DECLINED = "declined"
    REMOVED = "removed"


class WishlistCategory(str, enum.Enum):
    TECHNOLOGY = "technology"
    BOOKS = "books"
    FASHION = "fashion"
    HOME = "home"
    GAMES = "games"
    BEAUTY = "beauty"
    FOOD = "food"
    OTHER = "other"


class WishlistPriority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class GiftStatus(str, enum.Enum):
    NOT_STARTED = "not_started"
    SELECTED = "selected"
    PURCHASED = "purchased"
    PACKED = "packed"
    SHIPPED = "shipped"
    DELIVERED = "delivered"
    EXCHANGED = "exchanged"


class InvitationStatus(str, enum.Enum):
    PENDING = "pending"
    ACCEPTED = "accepted"
    EXPIRED = "expired"
    REVOKED = "revoked"


class NotificationType(str, enum.Enum):
    ASSIGNMENT = "assignment"
    INVITE = "invite"
    REMINDER = "reminder"
    GIFT_UPDATE = "gift_update"
    REVEAL = "reveal"
    SYSTEM = "system"
