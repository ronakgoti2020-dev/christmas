package com.secretsanta.app.ui.screens.gifts

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.LinearProgressIndicator
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FestiveCard
import com.secretsanta.app.ui.components.GoldChip

@Composable
fun GiftTrackingScreen(vm: AppViewModel, groupId: String) {
    val state by vm.state.collectAsState()
    LaunchedEffect(groupId) { vm.loadGiftTracking(groupId) }
    val steps = listOf("not_started", "selected", "purchased", "packed", "shipped", "delivered", "exchanged")
    Column(Modifier.padding(20.dp)) {
        Text("Gift tracking", style = MaterialTheme.typography.headlineMedium)
        Text("Organizers see progress only. Gift details stay with the giver until the reveal.")
        ErrorText(state.error)
        val done = state.giftProgress.count { it.gift_status == "exchanged" }
        if (state.giftProgress.isNotEmpty()) {
            LinearProgressIndicator(
                progress = { done.toFloat() / state.giftProgress.size },
                modifier = Modifier.padding(vertical = 16.dp)
            )
        }
        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp)) {
            items(state.giftProgress, key = { it.participant_id }) { row ->
                FestiveCard {
                    Text(row.full_name, style = MaterialTheme.typography.titleLarge)
                    GoldChip(row.gift_status.replace('_', ' '))
                    val index = steps.indexOf(row.gift_status).coerceAtLeast(0)
                    Text("Step ${index + 1} of ${steps.size}")
                }
            }
        }
    }
}
