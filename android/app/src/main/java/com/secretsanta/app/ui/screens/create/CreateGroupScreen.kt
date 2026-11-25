package com.secretsanta.app.ui.screens.create

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.FilterChip
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.data.api.GroupCreateRequest
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FormField
import com.secretsanta.app.ui.components.PrimaryButton
import java.time.LocalDate

@Composable
fun CreateGroupScreen(vm: AppViewModel, nav: NavController) {
    val state by vm.state.collectAsState()
    var step by remember { mutableStateOf(0) }
    var name by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var eventType by remember { mutableStateOf("christmas") }
    var eventDate by remember { mutableStateOf("2026-12-25") }
    var deadline by remember { mutableStateOf("2026-12-15") }
    var minBudget by remember { mutableStateOf("20") }
    var maxBudget by remember { mutableStateOf("50") }
    var currency by remember { mutableStateOf("USD") }
    var country by remember { mutableStateOf("India") }
    var exchange by remember { mutableStateOf("physical") }
    var privacy by remember { mutableStateOf("secret") }
    val types = listOf("christmas", "birthday", "office", "family", "friends", "new_year", "custom")
    val privacyModes = listOf("secret", "organizer", "public")

    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text("Create a gift exchange", style = MaterialTheme.typography.headlineMedium)
        Text("Step ${step + 1} of 3")
        Spacer(Modifier.height(16.dp))
        ErrorText(state.error)
        when (step) {
            0 -> {
                FormField(name, "Group name", { name = it })
                Spacer(Modifier.height(10.dp))
                FormField(description, "Description", { description = it }, singleLine = false)
                Spacer(Modifier.height(12.dp))
                Text("Occasion")
                WrapChips(types, eventType) { eventType = it }
                Spacer(Modifier.height(16.dp))
                PrimaryButton("Next") { if (name.length >= 2) step = 1 }
            }
            1 -> {
                FormField(eventDate, "Exchange date (YYYY-MM-DD)", { eventDate = it })
                Spacer(Modifier.height(10.dp))
                FormField(deadline, "Registration closes", { deadline = it })
                Spacer(Modifier.height(10.dp))
                FormField(minBudget, "Minimum budget", { minBudget = it })
                Spacer(Modifier.height(10.dp))
                FormField(maxBudget, "Maximum budget", { maxBudget = it })
                Spacer(Modifier.height(10.dp))
                FormField(currency, "Currency", { currency = it })
                Spacer(Modifier.height(10.dp))
                FormField(country, "Country", { country = it })
                Spacer(Modifier.height(16.dp))
                PrimaryButton("Next") { step = 2 }
            }
            else -> {
                Text("Exchange type")
                WrapChips(listOf("physical", "digital", "both"), exchange) { exchange = it }
                Spacer(Modifier.height(12.dp))
                Text("Privacy")
                WrapChips(privacyModes, privacy) { privacy = it }
                Text(
                    when (privacy) {
                        "secret" -> "Only the giver sees their recipient. The organizer cannot open the full mapping."
                        "organizer" -> "Participants see only their own recipient. You can see the full mapping."
                        else -> "Everyone in the group can see the assignments."
                    },
                    modifier = Modifier.padding(vertical = 12.dp)
                )
                PrimaryButton("Create group", enabled = !state.loading) {
                    vm.createGroup(
                        GroupCreateRequest(
                            name = name,
                            description = description.ifBlank { null },
                            event_type = eventType,
                            event_date = eventDate.ifBlank { LocalDate.now().plusMonths(1).toString() },
                            registration_deadline = deadline,
                            minimum_budget = minBudget.toDoubleOrNull() ?: 20.0,
                            maximum_budget = maxBudget.toDoubleOrNull() ?: 50.0,
                            currency = currency,
                            country = country,
                            exchange_type = exchange,
                            privacy_mode = privacy,
                            theme = if (eventType == "christmas") "christmas" else "classic"
                        )
                    ) { id -> nav.navigate("group/$id") { popUpTo("home") } }
                }
            }
        }
    }
}

@Composable
private fun WrapChips(options: List<String>, selected: String, onSelect: (String) -> Unit) {
    androidx.compose.foundation.layout.Row(
        modifier = Modifier.padding(top = 8.dp),
        horizontalArrangement = Arrangement.spacedBy(8.dp)
    ) { }
    options.forEach { option ->
        FilterChip(
            selected = option == selected,
            onClick = { onSelect(option) },
            label = { Text(option.replace('_', ' ')) },
            modifier = Modifier.padding(end = 8.dp, bottom = 8.dp)
        )
    }
}
