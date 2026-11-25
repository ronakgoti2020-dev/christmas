package com.secretsanta.app.data.api

import retrofit2.Response
import retrofit2.http.Body
import retrofit2.http.DELETE
import retrofit2.http.GET
import retrofit2.http.Header
import retrofit2.http.PATCH
import retrofit2.http.POST
import retrofit2.http.Path
import retrofit2.http.Query

interface SecretSantaApi {
    @POST("api/auth/register")
    suspend fun register(@Body body: RegisterRequest): TokenResponse

    @POST("api/auth/login")
    suspend fun login(@Body body: LoginRequest): TokenResponse

    @POST("api/auth/forgot-password")
    suspend fun forgotPassword(@Body body: ForgotPasswordRequest): MessageResponse

    @POST("api/auth/reset-password")
    suspend fun resetPassword(@Body body: ResetPasswordRequest): MessageResponse

    @POST("api/auth/verify-email")
    suspend fun verifyEmail(@Body body: VerifyEmailRequest): MessageResponse

    @GET("api/auth/me")
    suspend fun me(@Header("Authorization") auth: String): UserPublic

    @PATCH("api/auth/me")
    suspend fun updateMe(@Header("Authorization") auth: String, @Body body: ProfileUpdateRequest): UserPublic

    @GET("api/dashboard")
    suspend fun dashboard(@Header("Authorization") auth: String): DashboardResponse

    @GET("api/groups")
    suspend fun groups(@Header("Authorization") auth: String): List<GroupPublic>

    @POST("api/groups")
    suspend fun createGroup(@Header("Authorization") auth: String, @Body body: GroupCreateRequest): GroupPublic

    @GET("api/groups/{id}")
    suspend fun group(@Header("Authorization") auth: String, @Path("id") id: String): GroupPublic

    @PATCH("api/groups/{id}")
    suspend fun updateGroup(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: Map<String, @JvmSuppressWildcards Any>): GroupPublic

    @DELETE("api/groups/{id}")
    suspend fun cancelGroup(@Header("Authorization") auth: String, @Path("id") id: String): MessageResponse

    @GET("api/invitations/{code}")
    suspend fun previewInvite(@Path("code") code: String, @Header("Authorization") auth: String?): JoinPreview

    @POST("api/invitations/{code}/join")
    suspend fun join(@Path("code") code: String, @Header("Authorization") auth: String?, @Body body: JoinRequest): ParticipantPublic

    @GET("api/groups/{id}/participants")
    suspend fun participants(@Header("Authorization") auth: String, @Path("id") id: String): List<ParticipantPublic>

    @DELETE("api/groups/{id}/participants/{pid}")
    suspend fun removeParticipant(
        @Header("Authorization") auth: String,
        @Path("id") id: String,
        @Path("pid") pid: String
    ): MessageResponse

    @POST("api/groups/{id}/wishlist")
    suspend fun addWishlist(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: WishlistCreateRequest): WishlistPublic

    @GET("api/groups/{id}/wishlist")
    suspend fun wishlist(
        @Header("Authorization") auth: String,
        @Path("id") id: String,
        @Query("participant_id") participantId: String? = null
    ): List<WishlistPublic>

    @DELETE("api/groups/{id}/wishlist/{wid}")
    suspend fun deleteWishlist(
        @Header("Authorization") auth: String,
        @Path("id") id: String,
        @Path("wid") wid: String
    ): Response<Unit>

    @POST("api/groups/{id}/assignments/draw")
    suspend fun draw(@Header("Authorization") auth: String, @Path("id") id: String): DrawResponse

    @POST("api/groups/{id}/assignments/reset")
    suspend fun resetDraw(@Header("Authorization") auth: String, @Path("id") id: String): DrawResponse

    @GET("api/groups/{id}/assignments/me")
    suspend fun myAssignment(@Header("Authorization") auth: String, @Path("id") id: String): AssignmentMeResponse

    @PATCH("api/groups/{id}/gift-status")
    suspend fun updateGift(@Header("Authorization") auth: String, @Path("id") id: String, @Body body: GiftStatusUpdateRequest): MessageResponse

    @GET("api/groups/{id}/gift-tracking")
    suspend fun giftTracking(@Header("Authorization") auth: String, @Path("id") id: String): List<GiftProgressPublic>

    @GET("api/groups/{id}/reveal")
    suspend fun reveal(@Header("Authorization") auth: String, @Path("id") id: String): RevealState

    @POST("api/groups/{id}/reveal/messages")
    suspend fun revealMessage(
        @Header("Authorization") auth: String,
        @Path("id") id: String,
        @Body body: RevealMessageCreateRequest
    ): RevealMessagePublic

    @POST("api/groups/{id}/exclusions")
    suspend fun addExclusion(
        @Header("Authorization") auth: String,
        @Path("id") id: String,
        @Body body: ExclusionCreateRequest
    ): Map<String, Any>

    @POST("api/groups/{id}/invitations")
    suspend fun inviteEmail(
        @Header("Authorization") auth: String,
        @Path("id") id: String,
        @Body body: InvitationCreateRequest
    ): InvitationPublic

    @GET("api/notifications")
    suspend fun notifications(@Header("Authorization") auth: String): List<NotificationPublic>

    @PATCH("api/notifications/{id}/read")
    suspend fun readNotification(@Header("Authorization") auth: String, @Path("id") id: String): NotificationPublic

    @GET("api/public/how-it-works")
    suspend fun howItWorks(): HowItWorks

    @GET("api/public/gift-ideas")
    suspend fun giftIdeas(): GiftIdeas
}
