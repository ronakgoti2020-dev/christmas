package com.secretsanta.app.ui.screens.reveal

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
import com.secretsanta.app.ui.components.FestiveCard
import java.time.LocalDate
import java.time.temporal.ChronoUnit

@Composable
fun RevealScreen(vm: AppViewModel, groupId: String) {
    val state by vm.state.collectAsState()
    LaunchedEffect(groupId) { vm.loadReveal(groupId) }
    val reveal = state.reveal
    Column(Modifier.padding(20.dp)) {
        Text("Reveal night", style = MaterialTheme.typography.headlineMedium)
        if (reveal == null) {
            Text("Loading the event…")
            return
        }
        val days = runCatching { ChronoUnit.DAYS.between(LocalDate.now(), LocalDate.parse(reveal.event_date)) }.getOrDefault(0)
        FestiveCard {
            if (!reveal.unlocked) {
                Text("🎁")
                Text("$days days to go", style = MaterialTheme.typography.headlineMedium)
                Text("Gifts stay wrapped until ${reveal.event_date}.")
            } else {
                Text("It's time to open the gifts.")
                if (reveal.reveal_identities) {
                    reveal.identities.forEach { row ->
                        Text("${row["giver"]} → ${row["receiver"]}")
                    }
                } else {
                    Text("Identities stay secret unless the organizer turns reveal on.")
                }
            }
        }
        Spacer(Modifier.height(16.dp))
        Text("Group messages", style = MaterialTheme.typography.titleLarge)
        LazyColumn {
            items(reveal.messages, key = { it.id }) { message ->
                FestiveCard {
                    Text(message.author_name, style = MaterialTheme.typography.labelLarge)
                    Text(message.body)
                }
            }
        }
    }
}
