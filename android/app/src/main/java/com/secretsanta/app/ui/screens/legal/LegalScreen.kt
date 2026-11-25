package com.secretsanta.app.ui.screens.legal

import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.rememberScrollState
import androidx.compose.foundation.verticalScroll
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

@Composable
fun LegalScreen(title: String, vm: AppViewModel, mode: String) {
    val state by vm.state.collectAsState()
    LaunchedEffect(mode) {
        if (mode == "how") vm.loadHow()
        if (mode == "ideas") vm.loadIdeas()
    }
    Column(Modifier.verticalScroll(rememberScrollState()).padding(20.dp)) {
        Text(title, style = MaterialTheme.typography.headlineMedium)
        Spacer(Modifier.height(12.dp))
        when (mode) {
            "how" -> state.howSteps.forEach { step ->
                FestiveCard {
                    Text(step.title, style = MaterialTheme.typography.titleLarge)
                    Text(step.body)
                }
                Spacer(Modifier.height(10.dp))
            }
            "ideas" -> state.giftIdeas.forEach { collection ->
                FestiveCard {
                    Text(collection.title, style = MaterialTheme.typography.titleLarge)
                    collection.ideas.forEach { Text("• $it") }
                }
                Spacer(Modifier.height(10.dp))
            }
            "about" -> Text(
                "SecretSanta helps families, friends and offices run gift exchanges without leaking names. " +
                    "The Android app talks to the SecretSanta API. Assignments are created on the server in one " +
                    "transaction and stay hidden according to the group's privacy mode."
            )
            "privacy" -> Text(
                "We store the account details you give us, group membership, wishlists and gift assignments. " +
                    "Wishlists are visible only to you, your assigned giver, or the organizer if you allow it. " +
                    "We do not send private assignments, emails or gift preferences to analytics. " +
                    "You can ask for account deletion by writing to privacy@secretsanta.app."
            )
            "terms" -> Text(
                "SecretSanta is a coordination tool. You are responsible for the gifts you send and for following " +
                    "local law. Do not use the service to harass anyone. Organizers control draws and resets. " +
                    "We may suspend accounts that abuse invitations or scrape assignment data."
            )
            "contact" -> Text(
                "Email hello@secretsanta.app for product questions and privacy@secretsanta.app for data requests. " +
                    "We aim to reply within two business days."
            )
        }
    }
}
