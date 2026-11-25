package com.secretsanta.app.ui.screens.participants

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
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
import com.secretsanta.app.ui.components.GoldChip

@Composable
fun ParticipantsScreen(vm: AppViewModel, groupId: String) {
    val state by vm.state.collectAsState()
    LaunchedEffect(groupId) { vm.loadGroup(groupId) }
    Column(Modifier.padding(20.dp)) {
        Text("Participants", style = MaterialTheme.typography.headlineMedium)
        Text("${state.participants.size} joined")
        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.padding(top = 12.dp)) {
            items(state.participants, key = { it.id }) { person ->
                FestiveCard {
                    Text(person.full_name, style = MaterialTheme.typography.titleLarge)
                    Text(person.role.replaceFirstChar { it.uppercase() })
                    GoldChip(if (person.wishlist_completed) "Wishlist ready" else "Needs wishlist")
                    if (person.has_assignment) Text("Assigned")
                }
            }
        }
    }
}
