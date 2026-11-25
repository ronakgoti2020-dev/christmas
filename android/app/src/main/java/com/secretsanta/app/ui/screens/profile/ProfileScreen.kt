package com.secretsanta.app.ui.screens.profile

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.material3.TextButton
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
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FormField
import com.secretsanta.app.ui.components.PrimaryButton

@Composable
fun ProfileScreen(vm: AppViewModel, nav: NavController) {
    val state by vm.state.collectAsState()
    var name by remember { mutableStateOf(state.user?.full_name.orEmpty()) }
    var country by remember { mutableStateOf(state.user?.country.orEmpty()) }
    Column(Modifier.padding(20.dp)) {
        Text("Profile", style = MaterialTheme.typography.headlineMedium)
        Text(state.user?.email.orEmpty())
        Spacer(Modifier.height(16.dp))
        ErrorText(state.error)
        FormField(name, "Full name", { name = it })
        Spacer(Modifier.height(8.dp))
        FormField(country, "Country", { country = it })
        Spacer(Modifier.height(16.dp))
        PrimaryButton("Save") { vm.updateProfile(name, country) }
        TextButton({ nav.navigate("about") }) { Text("About") }
        TextButton({ nav.navigate("privacy") }) { Text("Privacy policy") }
        TextButton({ nav.navigate("terms") }) { Text("Terms") }
        TextButton({ nav.navigate("contact") }) { Text("Contact") }
        Spacer(Modifier.height(24.dp))
        TextButton({ vm.logout { nav.navigate("welcome") { popUpTo("home") { inclusive = true } } } }) {
            Text("Log out")
        }
    }
}
