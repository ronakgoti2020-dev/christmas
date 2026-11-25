package com.secretsanta.app.ui.navigation

import androidx.compose.foundation.layout.padding
import androidx.compose.material.icons.Icons
import androidx.compose.material.icons.outlined.Home
import androidx.compose.material.icons.outlined.Notifications
import androidx.compose.material.icons.outlined.Person
import androidx.compose.material3.Icon
import androidx.compose.material3.NavigationBar
import androidx.compose.material3.NavigationBarItem
import androidx.compose.material3.Scaffold
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.ui.Modifier
import androidx.lifecycle.viewmodel.compose.viewModel
import androidx.navigation.NavGraph.Companion.findStartDestination
import androidx.navigation.NavType
import androidx.navigation.compose.NavHost
import androidx.navigation.compose.composable
import androidx.navigation.compose.currentBackStackEntryAsState
import androidx.navigation.compose.rememberNavController
import androidx.navigation.navArgument
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.AppViewModelFactory
import com.secretsanta.app.SecretSantaApp
import com.secretsanta.app.ui.screens.assignment.AssignmentScreen
import com.secretsanta.app.ui.screens.auth.ForgotScreen
import com.secretsanta.app.ui.screens.auth.LoginScreen
import com.secretsanta.app.ui.screens.auth.RegisterScreen
import com.secretsanta.app.ui.screens.create.CreateGroupScreen
import com.secretsanta.app.ui.screens.dashboard.DashboardScreen
import com.secretsanta.app.ui.screens.gifts.GiftTrackingScreen
import com.secretsanta.app.ui.screens.groups.GroupDetailScreen
import com.secretsanta.app.ui.screens.join.JoinScreen
import com.secretsanta.app.ui.screens.legal.LegalScreen
import com.secretsanta.app.ui.screens.notifications.NotificationsScreen
import com.secretsanta.app.ui.screens.participants.ParticipantsScreen
import com.secretsanta.app.ui.screens.profile.ProfileScreen
import com.secretsanta.app.ui.screens.reveal.RevealScreen
import com.secretsanta.app.ui.screens.wishlist.WishlistScreen

@Composable
fun SecretSantaNav(app: SecretSantaApp, initialInvite: String?) {
    val nav = rememberNavController()
    val vm: AppViewModel = viewModel(factory = AppViewModelFactory(app))
    val state by vm.state.collectAsState()
    val start = if (state.token.isNullOrBlank()) "welcome" else "home"
    val tabs = listOf("home", "notifications", "profile")
    val route = nav.currentBackStackEntryAsState().value?.destination?.route.orEmpty()
    val showBar = route in tabs

    Scaffold(
        bottomBar = {
            if (showBar) {
                NavigationBar {
                    NavigationBarItem(
                        selected = route == "home",
                        onClick = { nav.navigate("home") { popUpTo(nav.graph.findStartDestination().id); launchSingleTop = true } },
                        icon = { Icon(Icons.Outlined.Home, contentDescription = "Home") },
                        label = { Text("Home") }
                    )
                    NavigationBarItem(
                        selected = route == "notifications",
                        onClick = { nav.navigate("notifications") { launchSingleTop = true } },
                        icon = { Icon(Icons.Outlined.Notifications, contentDescription = "Alerts") },
                        label = { Text("Alerts") }
                    )
                    NavigationBarItem(
                        selected = route == "profile",
                        onClick = { nav.navigate("profile") { launchSingleTop = true } },
                        icon = { Icon(Icons.Outlined.Person, contentDescription = "Profile") },
                        label = { Text("Profile") }
                    )
                }
            }
        }
    ) { padding ->
        NavHost(navController = nav, startDestination = if (initialInvite != null) "join/$initialInvite" else start, modifier = Modifier.padding(padding)) {
            composable("welcome") { LoginScreen(vm, nav, initialInvite) }
            composable("register") { RegisterScreen(vm, nav) }
            composable("forgot") { ForgotScreen(vm, nav) }
            composable("home") { DashboardScreen(vm, nav) }
            composable("create") { CreateGroupScreen(vm, nav) }
            composable("how") { LegalScreen(title = "How it works", vm = vm, mode = "how") }
            composable("ideas") { LegalScreen(title = "Gift ideas", vm = vm, mode = "ideas") }
            composable("about") { LegalScreen(title = "About", vm = vm, mode = "about") }
            composable("privacy") { LegalScreen(title = "Privacy policy", vm = vm, mode = "privacy") }
            composable("terms") { LegalScreen(title = "Terms", vm = vm, mode = "terms") }
            composable("contact") { LegalScreen(title = "Contact", vm = vm, mode = "contact") }
            composable("notifications") { NotificationsScreen(vm) }
            composable("profile") { ProfileScreen(vm, nav) }
            composable("join/{code}", arguments = listOf(navArgument("code") { type = NavType.StringType })) {
                JoinScreen(vm, nav, it.arguments?.getString("code").orEmpty())
            }
            composable("group/{id}", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
                GroupDetailScreen(vm, nav, it.arguments?.getString("id").orEmpty())
            }
            composable("group/{id}/participants", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
                ParticipantsScreen(vm, it.arguments?.getString("id").orEmpty())
            }
            composable("group/{id}/wishlist", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
                WishlistScreen(vm, it.arguments?.getString("id").orEmpty())
            }
            composable("group/{id}/assignment", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
                AssignmentScreen(vm, it.arguments?.getString("id").orEmpty())
            }
            composable("group/{id}/gifts", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
                GiftTrackingScreen(vm, it.arguments?.getString("id").orEmpty())
            }
            composable("group/{id}/reveal", arguments = listOf(navArgument("id") { type = NavType.StringType })) {
                RevealScreen(vm, it.arguments?.getString("id").orEmpty())
            }
        }
    }
}
