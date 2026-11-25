package com.secretsanta.app.ui.screens.join

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Row
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
import androidx.compose.material3.Checkbox
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Alignment
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.data.api.JoinRequest
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FestiveCard
import com.secretsanta.app.ui.components.FormField
import com.secretsanta.app.ui.components.LoadingPane
import com.secretsanta.app.ui.components.PrimaryButton

@Composable
fun JoinScreen(vm: AppViewModel, nav: NavController, code: String) {
    val state by vm.state.collectAsState()
    var preferences by remember { mutableStateOf("") }
    var interests by remember { mutableStateOf("") }
    var hobbies by remember { mutableStateOf("") }
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var ack by remember { mutableStateOf(true) }
    LaunchedEffect(code) { vm.previewInvite(code) }
    if (state.loading && state.joinPreview == null) {
        LoadingPane()
        return
    }
    val preview = state.joinPreview
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text("Join this exchange", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        ErrorText(state.error)
        if (preview != null) {
            FestiveCard {
                Text(preview.name, style = MaterialTheme.typography.titleLarge)
                Text("Hosted by ${preview.organizer_name}")
                Text("Budget ${preview.currency} ${preview.minimum_budget.toInt()}–${preview.maximum_budget.toInt()}")
                Text("Exchange on ${preview.event_date}")
                if (preview.closed) Text("Registration has closed.")
            }
        }
        Spacer(Modifier.height(16.dp))
        if (state.token.isNullOrBlank()) {
            FormField(name, "Full name", { name = it })
            Spacer(Modifier.height(8.dp))
            FormField(email, "Email", { email = it })
            Spacer(Modifier.height(8.dp))
            FormField(password, "Password", { password = it })
            Spacer(Modifier.height(8.dp))
        }
        FormField(preferences, "Gift preferences", { preferences = it }, singleLine = false)
        Spacer(Modifier.height(8.dp))
        FormField(interests, "Interests", { interests = it })
        Spacer(Modifier.height(8.dp))
        FormField(hobbies, "Hobbies", { hobbies = it })
        Row(verticalAlignment = Alignment.CenterVertically) {
            Checkbox(checked = ack, onCheckedChange = { ack = it })
            Text("I accept the gift budget")
        }
        PrimaryButton("Join group", enabled = ack && preview?.closed != true && !state.loading) {
            vm.join(
                code,
                JoinRequest(
                    gift_preferences = preferences.ifBlank { null },
                    interests = interests.ifBlank { null },
                    hobbies = hobbies.ifBlank { null },
                    budget_acknowledged = ack,
                    shipping_address = null,
                    country = preview?.country,
                    full_name = name.ifBlank { null },
                    email = email.ifBlank { null },
                    password = password.ifBlank { null }
                )
            ) { nav.navigate("home") { popUpTo("welcome") { inclusive = true } } }
        }
    }
}
