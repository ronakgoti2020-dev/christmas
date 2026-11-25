package com.secretsanta.app.ui.screens.groups

import android.content.Intent
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.platform.LocalContext
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FestiveCard
import com.secretsanta.app.ui.components.GoldChip
import com.secretsanta.app.ui.components.LoadingPane
import com.secretsanta.app.ui.components.PrimaryButton

@Composable
fun GroupDetailScreen(vm: AppViewModel, nav: NavController, groupId: String) {
    val state by vm.state.collectAsState()
    val context = LocalContext.current
    LaunchedEffect(groupId) { vm.loadGroup(groupId) }
    val group = state.group
    if (group == null) {
        if (state.loading) LoadingPane() else ErrorText(state.error ?: "Group not found")
        return
    }
    val isOrganizer = group.organizer_id == state.user?.id
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp), verticalArrangement = Arrangement.spacedBy(12.dp)) {
        GoldChip(group.event_type.replace('_', ' '))
        Text(group.name, style = MaterialTheme.typography.headlineMedium)
        Text(group.description.orEmpty())
        FestiveCard {
            Text("Budget ${group.currency} ${group.minimum_budget.toInt()}–${group.maximum_budget.toInt()}")
            Text("Exchange ${group.event_date}")
            Text("Registration until ${group.registration_deadline}")
            Text("${state.participants.size} participants · ${state.participants.count { it.wishlist_completed }} wishlists ready")
            Text("Privacy: ${group.privacy_mode}")
        }
        ErrorText(state.error)
        if (!state.success.isNullOrBlank()) Text(state.success!!)
        PrimaryButton("My wishlist") { nav.navigate("group/$groupId/wishlist") }
        PrimaryButton("My assignment") { nav.navigate("group/$groupId/assignment") }
        PrimaryButton("Gift tracking") { nav.navigate("group/$groupId/gifts") }
        PrimaryButton("Reveal event") { nav.navigate("group/$groupId/reveal") }
        TextButton({ nav.navigate("group/$groupId/participants") }) { Text("View participants") }
        if (isOrganizer) {
            Spacer(Modifier.height(8.dp))
            Text("Organizer tools", style = MaterialTheme.typography.titleLarge)
            val link = group.invite_url ?: "https://secretsanta.app/join/${group.invite_code}"
            FestiveCard {
                Text("Invite link")
                Text(link)
            }
            PrimaryButton("Share invite") {
                val send = Intent(Intent.ACTION_SEND).apply {
                    type = "text/plain"
                    putExtra(Intent.EXTRA_TEXT, "Join my Secret Santa group: $link")
                }
                context.startActivity(Intent.createChooser(send, "Share invite"))
            }
            if (group.assignment_status != "completed") {
                PrimaryButton("Start the draw", enabled = state.participants.size >= 2 && !state.loading) {
                    vm.draw(groupId)
                }
            }
            TextButton({ vm.cancelGroup(groupId) { nav.navigate("home") } }) { Text("Cancel group") }
        }
    }
}
