package com.secretsanta.app

import androidx.lifecycle.ViewModel
import androidx.lifecycle.ViewModelProvider
import androidx.lifecycle.viewModelScope
import com.secretsanta.app.data.api.AssignmentMeResponse
import com.secretsanta.app.data.api.DashboardResponse
import com.secretsanta.app.data.api.GiftCollection
import com.secretsanta.app.data.api.ForgotPasswordRequest
import com.secretsanta.app.data.api.GiftStatusUpdateRequest
import com.secretsanta.app.data.api.GroupCreateRequest
import com.secretsanta.app.data.api.GroupPublic
import com.secretsanta.app.data.api.HowStep
import com.secretsanta.app.data.api.JoinPreview
import com.secretsanta.app.data.api.JoinRequest
import com.secretsanta.app.data.api.LoginRequest
import com.secretsanta.app.data.api.NotificationPublic
import com.secretsanta.app.data.api.ParticipantPublic
import com.secretsanta.app.data.api.ProfileUpdateRequest
import com.secretsanta.app.data.api.RegisterRequest
import com.secretsanta.app.data.api.RevealState
import com.secretsanta.app.data.api.UserPublic
import com.secretsanta.app.data.api.WishlistCreateRequest
import com.secretsanta.app.data.api.WishlistPublic
import com.secretsanta.app.data.api.bearer
import kotlinx.coroutines.flow.MutableStateFlow
import kotlinx.coroutines.flow.StateFlow
import kotlinx.coroutines.flow.first
import kotlinx.coroutines.launch
import retrofit2.HttpException

data class UiState(
    val loading: Boolean = false,
    val error: String? = null,
    val token: String? = null,
    val user: UserPublic? = null,
    val dashboard: DashboardResponse? = null,
    val group: GroupPublic? = null,
    val participants: List<ParticipantPublic> = emptyList(),
    val wishlist: List<WishlistPublic> = emptyList(),
    val assignment: AssignmentMeResponse? = null,
    val notifications: List<NotificationPublic> = emptyList(),
    val joinPreview: JoinPreview? = null,
    val howSteps: List<HowStep> = emptyList(),
    val giftIdeas: List<GiftCollection> = emptyList(),
    val reveal: RevealState? = null,
    val giftProgress: List<com.secretsanta.app.data.api.GiftProgressPublic> = emptyList(),
    val success: String? = null
)

class AppViewModel(private val app: SecretSantaApp) : ViewModel() {
    private val _state = MutableStateFlow(UiState())
    val state: StateFlow<UiState> = _state

    init {
        viewModelScope.launch {
            val token = app.tokenStore.token.first()
            if (!token.isNullOrBlank()) {
                _state.value = _state.value.copy(token = token)
                runCatching { app.api.me(bearer(token)) }
                    .onSuccess { _state.value = _state.value.copy(user = it) }
                    .onFailure { app.tokenStore.clear(); _state.value = UiState() }
            }
        }
    }

    private fun auth(): String = bearer(_state.value.token ?: "")

    private suspend fun <T> wrap(block: suspend () -> T): T? {
        _state.value = _state.value.copy(loading = true, error = null, success = null)
        return try {
            val result = block()
            _state.value = _state.value.copy(loading = false)
            result
        } catch (ex: HttpException) {
            val raw = ex.response()?.errorBody()?.string().orEmpty()
            _state.value = _state.value.copy(loading = false, error = raw.ifBlank { ex.message() })
            null
        } catch (ex: Exception) {
            _state.value = _state.value.copy(loading = false, error = ex.message ?: "Something went wrong")
            null
        }
    }

    fun login(email: String, password: String, onDone: () -> Unit) = viewModelScope.launch {
        val result = wrap { app.api.login(LoginRequest(email, password)) } ?: return@launch
        app.tokenStore.saveToken(result.access_token)
        _state.value = _state.value.copy(token = result.access_token, user = result.user)
        onDone()
    }

    fun register(name: String, email: String, password: String, country: String, onDone: () -> Unit) =
        viewModelScope.launch {
            val result = wrap {
                app.api.register(RegisterRequest(name, email, password, country.ifBlank { null }))
            } ?: return@launch
            app.tokenStore.saveToken(result.access_token)
            _state.value = _state.value.copy(token = result.access_token, user = result.user)
            onDone()
        }

    fun forgotPassword(email: String) = viewModelScope.launch {
        wrap { app.api.forgotPassword(ForgotPasswordRequest(email)) } ?: return@launch
        _state.value = _state.value.copy(success = "If that email is registered, a reset code is on its way.")
    }

    fun logout(onDone: () -> Unit) = viewModelScope.launch {
        app.tokenStore.clear()
        _state.value = UiState()
        onDone()
    }

    fun loadDashboard() = viewModelScope.launch {
        val dash = wrap { app.api.dashboard(auth()) } ?: return@launch
        _state.value = _state.value.copy(dashboard = dash, user = dash.user)
    }

    fun createGroup(body: GroupCreateRequest, onDone: (String) -> Unit) = viewModelScope.launch {
        val group = wrap { app.api.createGroup(auth(), body) } ?: return@launch
        _state.value = _state.value.copy(group = group, success = "Group created")
        onDone(group.id)
    }

    fun loadGroup(id: String) = viewModelScope.launch {
        val group = wrap { app.api.group(auth(), id) } ?: return@launch
        val people = wrap { app.api.participants(auth(), id) } ?: emptyList()
        _state.value = _state.value.copy(group = group, participants = people)
    }

    fun loadWishlist(id: String, participantId: String? = null) = viewModelScope.launch {
        val items = wrap { app.api.wishlist(auth(), id, participantId) } ?: return@launch
        _state.value = _state.value.copy(wishlist = items)
    }

    fun addWishlist(id: String, body: WishlistCreateRequest) = viewModelScope.launch {
        wrap { app.api.addWishlist(auth(), id, body) } ?: return@launch
        loadWishlist(id)
        _state.value = _state.value.copy(success = "Gift idea saved")
    }

    fun previewInvite(code: String) = viewModelScope.launch {
        val token = _state.value.token
        val preview = wrap { app.api.previewInvite(code, token?.let(::bearer)) } ?: return@launch
        _state.value = _state.value.copy(joinPreview = preview)
    }

    fun join(code: String, body: JoinRequest, onDone: () -> Unit) = viewModelScope.launch {
        val token = _state.value.token
        val result = wrap { app.api.join(code, token?.let(::bearer), body) } ?: return@launch
        if (!result.access_token.isNullOrBlank()) {
            app.tokenStore.saveToken(result.access_token)
            _state.value = _state.value.copy(token = result.access_token)
        }
        _state.value = _state.value.copy(success = "You're in")
        onDone()
    }

    fun draw(id: String) = viewModelScope.launch {
        val result = wrap { app.api.draw(auth(), id) } ?: return@launch
        _state.value = _state.value.copy(success = result.message)
        loadGroup(id)
    }

    fun loadAssignment(id: String) = viewModelScope.launch {
        val assignment = wrap { app.api.myAssignment(auth(), id) } ?: return@launch
        _state.value = _state.value.copy(assignment = assignment, wishlist = assignment.wishlist)
    }

    fun updateGift(id: String, status: String) = viewModelScope.launch {
        wrap { app.api.updateGift(auth(), id, GiftStatusUpdateRequest(status)) } ?: return@launch
        loadAssignment(id)
        _state.value = _state.value.copy(success = "Gift status updated")
    }

    fun loadGiftTracking(id: String) = viewModelScope.launch {
        val rows = wrap { app.api.giftTracking(auth(), id) } ?: return@launch
        _state.value = _state.value.copy(giftProgress = rows)
    }

    fun loadNotifications() = viewModelScope.launch {
        val rows = wrap { app.api.notifications(auth()) } ?: return@launch
        _state.value = _state.value.copy(notifications = rows)
    }

    fun loadHow() = viewModelScope.launch {
        val data = wrap { app.api.howItWorks() } ?: return@launch
        _state.value = _state.value.copy(howSteps = data.steps)
    }

    fun loadIdeas() = viewModelScope.launch {
        val data = wrap { app.api.giftIdeas() } ?: return@launch
        _state.value = _state.value.copy(giftIdeas = data.collections)
    }

    fun loadReveal(id: String) = viewModelScope.launch {
        val data = wrap { app.api.reveal(auth(), id) } ?: return@launch
        _state.value = _state.value.copy(reveal = data)
    }

    fun updateProfile(name: String, country: String) = viewModelScope.launch {
        val user = wrap { app.api.updateMe(auth(), ProfileUpdateRequest(name, country, null)) } ?: return@launch
        _state.value = _state.value.copy(user = user, success = "Profile saved")
    }

    fun cancelGroup(id: String, onDone: () -> Unit) = viewModelScope.launch {
        wrap { app.api.cancelGroup(auth(), id) } ?: return@launch
        onDone()
    }
}

class AppViewModelFactory(private val app: SecretSantaApp) : ViewModelProvider.Factory {
    @Suppress("UNCHECKED_CAST")
    override fun <T : ViewModel> create(modelClass: Class<T>): T = AppViewModel(app) as T
}
