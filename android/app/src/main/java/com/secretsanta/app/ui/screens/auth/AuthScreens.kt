package com.secretsanta.app.ui.screens.auth

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.foundation.layout.fillMaxWidth
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
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.text.input.PasswordVisualTransformation
import androidx.compose.ui.unit.dp
import androidx.navigation.NavController
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FormField
import com.secretsanta.app.ui.components.PrimaryButton
import androidx.compose.material3.OutlinedTextField

@Composable
fun LoginScreen(vm: AppViewModel, nav: NavController, initialInvite: String?) {
    val state by vm.state.collectAsState()
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    LaunchedEffect(state.token) {
        if (!state.token.isNullOrBlank()) {
            nav.navigate("home") { popUpTo("welcome") { inclusive = true } }
        }
    }
    Column(
        Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp),
        verticalArrangement = Arrangement.Center
    ) {
        Text("🎅 SecretSanta", style = MaterialTheme.typography.headlineLarge)
        Spacer(Modifier.height(8.dp))
        Text("Organize a gift exchange without the spreadsheet chaos.")
        Spacer(Modifier.height(24.dp))
        ErrorText(state.error)
        FormField(email, "Email", { email = it })
        Spacer(Modifier.height(12.dp))
        OutlinedTextField(
            value = password,
            onValueChange = { password = it },
            label = { Text("Password") },
            visualTransformation = PasswordVisualTransformation(),
            modifier = Modifier.fillMaxWidth(),
            singleLine = true
        )
        Spacer(Modifier.height(20.dp))
        PrimaryButton("Sign in", enabled = !state.loading) { vm.login(email, password) {} }
        TextButton({ nav.navigate("register") }) { Text("Create an account") }
        TextButton({ nav.navigate("forgot") }) { Text("Forgot password") }
        TextButton({ nav.navigate("how") }) { Text("How it works") }
        if (!initialInvite.isNullOrBlank()) {
            TextButton({ nav.navigate("join/$initialInvite") }) { Text("Open invitation") }
        }
    }
}

@Composable
fun RegisterScreen(vm: AppViewModel, nav: NavController) {
    val state by vm.state.collectAsState()
    var name by remember { mutableStateOf("") }
    var email by remember { mutableStateOf("") }
    var password by remember { mutableStateOf("") }
    var country by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize().verticalScroll(rememberScrollState()).padding(24.dp)) {
        Text("Join SecretSanta", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(16.dp))
        ErrorText(state.error)
        FormField(name, "Full name", { name = it })
        Spacer(Modifier.height(10.dp))
        FormField(email, "Email", { email = it })
        Spacer(Modifier.height(10.dp))
        FormField(password, "Password (mixed case + number)", { password = it })
        Spacer(Modifier.height(10.dp))
        FormField(country, "Country", { country = it })
        Spacer(Modifier.height(20.dp))
        PrimaryButton("Create account", enabled = !state.loading) {
            vm.register(name, email, password, country) {
                nav.navigate("home") { popUpTo("welcome") { inclusive = true } }
            }
        }
        TextButton({ nav.popBackStack() }) { Text("Already have an account") }
    }
}

@Composable
fun ForgotScreen(vm: AppViewModel, nav: NavController) {
    val state by vm.state.collectAsState()
    var email by remember { mutableStateOf("") }
    Column(Modifier.fillMaxSize().padding(24.dp), verticalArrangement = Arrangement.Center) {
        Text("Reset password", style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        ErrorText(state.error)
        FormField(email, "Email", { email = it })
        Spacer(Modifier.height(16.dp))
        PrimaryButton("Send reset code") { vm.forgotPassword(email) }
        if (!state.success.isNullOrBlank()) Text(state.success!!)
        TextButton({ nav.popBackStack() }) { Text("Back") }
    }
}
