package com.secretsanta.app.ui.screens.dashboard

import androidx.compose.foundation.clickable
import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.ui.components.EmptyPane
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FestiveCard
import com.secretsanta.app.ui.components.GoldChip
import com.secretsanta.app.ui.components.LoadingPane
import com.secretsanta.app.ui.components.PrimaryButton
import java.time.LocalDate
import java.time.temporal.ChronoUnit

@Composable
fun DashboardScreen(vm: AppViewModel, nav: NavController) {
    val state by vm.state.collectAsState()
    LaunchedEffect(Unit) { vm.loadDashboard() }
    if (state.loading && state.dashboard == null) {
        LoadingPane()
        return
    }
    val dash = state.dashboard
    Column(Modifier.fillMaxSize().padding(20.dp)) {
        Text("Hello ${dash?.user?.full_name ?: ""}", style = MaterialTheme.typography.headlineMedium)
        Text("Your gift exchanges for 2026 and beyond.")
        Spacer(Modifier.height(16.dp))
        PrimaryButton("Create a Gift Exchange") { nav.navigate("create") }
        Spacer(Modifier.height(8.dp))
        Row(horizontalArrangement = Arrangement.spacedBy(8.dp)) {
            TextButton({ nav.navigate("how") }) { Text("How it works") }
            TextButton({ nav.navigate("ideas") }) { Text("Gift ideas") }
        }
        ErrorText(state.error)
        if (dash == null || dash.active_groups.isEmpty()) {
            EmptyPane(
                "No exchanges yet",
                "Create a group, share the invite link, then draw names when everyone has joined."
            )
            return
        }
        Spacer(Modifier.height(8.dp))
        Text("${dash.unread_notifications} unread alerts")
        LazyColumn(verticalArrangement = Arrangement.spacedBy(12.dp), modifier = Modifier.padding(top = 12.dp)) {
            items(dash.active_groups, key = { it.id }) { group ->
                FestiveCard(Modifier.clickable { nav.navigate("group/${group.id}") }) {
                    GoldChip(group.event_type.replaceFirstChar { it.uppercase() })
                    Spacer(Modifier.height(8.dp))
                    Text(group.name, style = MaterialTheme.typography.titleLarge)
                    Text("${group.currency} ${group.minimum_budget.toInt()}–${group.maximum_budget.toInt()} · ${group.participant_count} people")
                    val days = runCatching {
                        ChronoUnit.DAYS.between(LocalDate.now(), LocalDate.parse(group.event_date))
                    }.getOrDefault(0)
                    Text(if (days >= 0) "$days days until the exchange" else "Exchange date has passed")
                    Text("Assignment: ${group.assignment_status.replace('_', ' ')}")
                }
            }
        }
    }
}
