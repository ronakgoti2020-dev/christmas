package com.secretsanta.app.ui.screens.notifications

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
import com.secretsanta.app.ui.components.EmptyPane
import com.secretsanta.app.ui.components.FestiveCard

@Composable
fun NotificationsScreen(vm: AppViewModel) {
    val state by vm.state.collectAsState()
    LaunchedEffect(Unit) { vm.loadNotifications() }
    Column(Modifier.padding(20.dp)) {
        Text("Notifications", style = MaterialTheme.typography.headlineMedium)
        if (state.notifications.isEmpty()) {
            EmptyPane("You're all caught up", "Draws, invites and reminders will land here. Assignment emails stay off this preview.")
            return
        }
        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.padding(top = 12.dp)) {
            items(state.notifications, key = { it.id }) { item ->
                FestiveCard {
                    Text(item.title, style = MaterialTheme.typography.titleLarge)
                    Text(item.message)
                    Text(item.created_at)
                }
            }
        }
    }
}
