package com.secretsanta.app.ui.screens.assignment

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.ui.components.EmptyPane
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FestiveCard
import com.secretsanta.app.ui.components.GoldChip
import com.secretsanta.app.ui.components.PrimaryButton

private val giftStatuses = listOf(
    "not_started", "selected", "purchased", "packed", "shipped", "delivered", "exchanged"
)

@Composable
fun AssignmentScreen(vm: AppViewModel, groupId: String) {
    val state by vm.state.collectAsState()
    LaunchedEffect(groupId) { vm.loadAssignment(groupId) }
    val assignment = state.assignment
    Column(Modifier.padding(20.dp)) {
        Text("Your Secret Santa assignment", style = MaterialTheme.typography.headlineMedium)
        ErrorText(state.error)
        if (assignment == null) {
            EmptyPane("Not drawn yet", "Wait for the organizer to start the random draw. Assignments stay private.")
            return
        }
        FestiveCard {
            Text("You are giving a gift to", style = MaterialTheme.typography.labelLarge)
            Text(assignment.receiver_name, style = MaterialTheme.typography.headlineMedium)
            Text("Budget ${assignment.currency} ${assignment.budget_min.toInt()}–${assignment.budget_max.toInt()}")
            Text("Exchange ${assignment.event_date}")
            if (!assignment.receiver_preferences.isNullOrBlank()) Text("Preferences: ${assignment.receiver_preferences}")
            if (!assignment.receiver_interests.isNullOrBlank()) Text("Interests: ${assignment.receiver_interests}")
        }
        Spacer(Modifier.height(12.dp))
        Text("Keep this screen private. Don't screenshot it into a group chat.")
        Spacer(Modifier.height(12.dp))
        Text("Gift status: ${assignment.gift_status ?: "not_started"}")
        giftStatuses.forEach { status ->
            androidx.compose.material3.TextButton(onClick = { vm.updateGift(groupId, status) }) {
                Text(status.replace('_', ' '))
            }
        }
        Spacer(Modifier.height(8.dp))
        Text("Their wishlist", style = MaterialTheme.typography.titleLarge)
        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            items(assignment.wishlist, key = { it.id }) { item ->
                FestiveCard {
                    GoldChip(item.priority)
                    Text(item.title, style = MaterialTheme.typography.titleLarge)
                    Text(item.description.orEmpty())
                    Text(item.product_url.orEmpty())
                }
            }
        }
        if (assignment.wishlist.isEmpty()) Text("They have not added wishlist ideas yet.")
        PrimaryButton("Refresh") { vm.loadAssignment(groupId) }
    }
}
