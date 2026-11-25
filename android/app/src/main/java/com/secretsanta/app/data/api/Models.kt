package com.secretsanta.app.data.api

data class TokenResponse(
    val access_token: String,
    val token_type: String?,
    val user: UserPublic
)

data class UserPublic(
    val id: String,
    val full_name: String,
    val email: String,
    val profile_image: String?,
    val country: String?,
    val email_verified: Boolean
)

data class RegisterRequest(
    val full_name: String,
    val email: String,
    val password: String,
    val country: String?
)

data class LoginRequest(val email: String, val password: String)

data class ForgotPasswordRequest(val email: String)
data class ResetPasswordRequest(val token: String, val password: String)
data class VerifyEmailRequest(val token: String)
data class ProfileUpdateRequest(val full_name: String?, val country: String?, val profile_image: String?)

data class GroupPublic(
    val id: String,
    val name: String,
    val slug: String,
    val description: String?,
    val event_type: String,
    val event_date: String,
    val registration_deadline: String,
    val minimum_budget: Double,
    val maximum_budget: Double,
    val currency: String,
    val country: String,
    val exchange_type: String,
    val privacy_mode: String,
    val visibility: String,
    val organizer_id: String,
    val invite_code: String,
    val invite_url: String?,
    val status: String,
    val assignment_status: String,
    val reveal_identities: Boolean,
    val theme: String,
    val participant_count: Int,
    val created_at: String?
)

data class GroupCreateRequest(
    val name: String,
    val description: String?,
    val event_type: String,
    val event_date: String,
    val registration_deadline: String,
    val minimum_budget: Double,
    val maximum_budget: Double,
    val currency: String,
    val country: String,
    val exchange_type: String,
    val privacy_mode: String,
    val visibility: String = "private",
    val reveal_identities: Boolean = false,
    val theme: String = "christmas"
)

data class DashboardResponse(
    val user: UserPublic,
    val active_groups: List<GroupPublic>,
    val upcoming_exchanges: List<GroupPublic>,
    val pending_invites: Int,
    val unread_notifications: Int
)

data class JoinPreview(
    val name: String,
    val description: String?,
    val event_type: String,
    val event_date: String,
    val registration_deadline: String,
    val minimum_budget: Double,
    val maximum_budget: Double,
    val currency: String,
    val country: String,
    val exchange_type: String,
    val organizer_name: String,
    val already_joined: Boolean,
    val closed: Boolean
)

data class JoinRequest(
    val gift_preferences: String?,
    val interests: String?,
    val hobbies: String?,
    val budget_acknowledged: Boolean,
    val shipping_address: String?,
    val country: String?,
    val full_name: String?,
    val email: String?,
    val password: String?
)

data class ParticipantPublic(
    val id: String,
    val user_id: String,
    val full_name: String,
    val email: String?,
    val profile_image: String?,
    val country: String?,
    val role: String,
    val participation_status: String,
    val wishlist_completed: Boolean,
    val has_assignment: Boolean,
    val joined_at: String,
    val gift_preferences: String?,
    val interests: String?,
    val hobbies: String?,
    val access_token: String?
)

data class WishlistPublic(
    val id: String,
    val group_id: String,
    val participant_id: String,
    val title: String,
    val description: String?,
    val product_url: String?,
    val image_url: String?,
    val estimated_price: Double?,
    val priority: String,
    val category: String,
    val created_at: String
)

data class WishlistCreateRequest(
    val title: String,
    val description: String?,
    val product_url: String?,
    val estimated_price: Double?,
    val priority: String,
    val category: String
)

data class AssignmentMeResponse(
    val assignment_id: String,
    val group_id: String,
    val receiver_participant_id: String,
    val receiver_name: String,
    val receiver_country: String?,
    val receiver_preferences: String?,
    val receiver_interests: String?,
    val receiver_hobbies: String?,
    val budget_min: Double,
    val budget_max: Double,
    val currency: String,
    val event_date: String,
    val wishlist: List<WishlistPublic>,
    val gift_status: String?
)

data class DrawResponse(val assigned_count: Int, val message: String)
data class MessageResponse(val message: String)
data class GiftStatusUpdateRequest(
    val gift_status: String,
    val gift_description: String? = null,
    val tracking_reference: String? = null
)
data class GiftProgressPublic(
    val participant_id: String,
    val full_name: String,
    val gift_status: String,
    val updated_at: String?
)
data class NotificationPublic(
    val id: String,
    val group_id: String?,
    val notification_type: String,
    val title: String,
    val message: String,
    val deep_link: String?,
    val read_at: String?,
    val created_at: String
)
data class HowItWorks(val title: String, val steps: List<HowStep>)
data class HowStep(val title: String, val body: String)
data class GiftIdeas(val title: String, val collections: List<GiftCollection>)
data class GiftCollection(val slug: String, val title: String, val ideas: List<String>)
data class ExclusionCreateRequest(
    val participant_id: String,
    val excluded_participant_id: String,
    val reason: String?
)
data class InvitationCreateRequest(val email: String?, val expires_in_days: Int = 21)
data class InvitationPublic(
    val id: String,
    val invitation_email: String?,
    val invitation_code: String,
    val status: String,
    val invite_url: String?
)
data class RevealMessagePublic(val id: String, val author_name: String, val body: String, val created_at: String)
data class RevealMessageCreateRequest(val body: String)
data class RevealState(
    val event_date: String,
    val unlocked: Boolean,
    val reveal_identities: Boolean,
    val identities: List<Map<String, String>>,
    val messages: List<RevealMessagePublic>
)
data class ApiError(val detail: Any?)
