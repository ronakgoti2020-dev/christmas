package com.secretsanta.app

import android.os.Bundle
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.activity.enableEdgeToEdge
import com.secretsanta.app.ui.navigation.SecretSantaNav
import com.secretsanta.app.ui.theme.SecretSantaTheme

class MainActivity : ComponentActivity() {
    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)
        enableEdgeToEdge()
        val app = application as SecretSantaApp
        val invite = intent?.data?.lastPathSegment
        setContent {
            SecretSantaTheme {
                SecretSantaNav(app = app, initialInvite = invite)
            }
        }
    }
}
