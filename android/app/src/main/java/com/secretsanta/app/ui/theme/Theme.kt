package com.secretsanta.app.ui.theme

import androidx.compose.foundation.isSystemInDarkTheme
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.darkColorScheme
import androidx.compose.material3.lightColorScheme
import androidx.compose.runtime.Composable
import androidx.compose.ui.graphics.Color
import androidx.compose.ui.text.font.FontFamily
import androidx.compose.ui.text.font.FontWeight
import androidx.compose.material3.Typography
import androidx.compose.ui.text.TextStyle
import androidx.compose.ui.unit.sp

val DeepRed = Color(0xFF8B1E3F)
val Evergreen = Color(0xFF1B4332)
val Gold = Color(0xFFC9A227)
val Cream = Color(0xFFFFF7F2)
val Snow = Color(0xFFFFFFFF)
val Pine = Color(0xFF2D6A4F)
val Night = Color(0xFF1A1020)

private val LightColors = lightColorScheme(
    primary = DeepRed,
    onPrimary = Snow,
    secondary = Evergreen,
    onSecondary = Snow,
    tertiary = Gold,
    background = Cream,
    surface = Snow,
    onBackground = Night,
    onSurface = Night,
    error = Color(0xFFB3261E)
)

private val DarkColors = darkColorScheme(
    primary = Color(0xFFE07A93),
    onPrimary = Night,
    secondary = Color(0xFF95D5B2),
    background = Color(0xFF140E16),
    surface = Color(0xFF221826),
    onBackground = Cream,
    onSurface = Cream,
    tertiary = Gold
)

private val AppTypography = Typography(
    headlineLarge = TextStyle(fontFamily = FontFamily.Serif, fontWeight = FontWeight.Bold, fontSize = 32.sp),
    headlineMedium = TextStyle(fontFamily = FontFamily.Serif, fontWeight = FontWeight.SemiBold, fontSize = 24.sp),
    titleLarge = TextStyle(fontWeight = FontWeight.SemiBold, fontSize = 20.sp),
    bodyLarge = TextStyle(fontSize = 16.sp, lineHeight = 22.sp),
    labelLarge = TextStyle(fontWeight = FontWeight.Medium, fontSize = 14.sp)
)

@Composable
fun SecretSantaTheme(
    festive: Boolean = true,
    darkTheme: Boolean = isSystemInDarkTheme(),
    content: @Composable () -> Unit
) {
    MaterialTheme(
        colorScheme = if (darkTheme && !festive) DarkColors else LightColors,
        typography = AppTypography,
        content = content
    )
}
