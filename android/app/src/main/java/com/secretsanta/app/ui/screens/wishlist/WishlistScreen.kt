package com.secretsanta.app.ui.screens.wishlist

import androidx.compose.foundation.layout.Arrangement
import androidx.compose.foundation.layout.Column
import androidx.compose.foundation.layout.Spacer
import androidx.compose.foundation.layout.height
import androidx.compose.foundation.layout.padding
import androidx.compose.foundation.lazy.LazyColumn
import androidx.compose.foundation.lazy.items
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Text
import androidx.compose.runtime.Composable
import androidx.compose.runtime.LaunchedEffect
import androidx.compose.runtime.collectAsState
import androidx.compose.runtime.getValue
import androidx.compose.runtime.mutableStateOf
import androidx.compose.runtime.remember
import androidx.compose.runtime.setValue
import androidx.compose.ui.Modifier
import androidx.compose.ui.unit.dp
import com.secretsanta.app.AppViewModel
import com.secretsanta.app.data.api.WishlistCreateRequest
import com.secretsanta.app.ui.components.ErrorText
import com.secretsanta.app.ui.components.FestiveCard
import com.secretsanta.app.ui.components.FormField
import com.secretsanta.app.ui.components.GoldChip
import com.secretsanta.app.ui.components.PrimaryButton

@Composable
fun WishlistScreen(vm: AppViewModel, groupId: String) {
    val state by vm.state.collectAsState()
    var title by remember { mutableStateOf("") }
    var description by remember { mutableStateOf("") }
    var url by remember { mutableStateOf("") }
    var price by remember { mutableStateOf("") }
    LaunchedEffect(groupId) { vm.loadWishlist(groupId) }
    Column(Modifier.padding(20.dp)) {
        Text("Your wishlist", style = MaterialTheme.typography.headlineMedium)
        Text("Only your Secret Santa can see these ideas after the draw.")
        Spacer(Modifier.height(12.dp))
        ErrorText(state.error)
        FormField(title, "Gift name", { title = it })
        Spacer(Modifier.height(8.dp))
        FormField(description, "Description", { description = it })
        Spacer(Modifier.height(8.dp))
        FormField(url, "Product URL", { url = it })
        Spacer(Modifier.height(8.dp))
        FormField(price, "Estimated price", { price = it })
        Spacer(Modifier.height(12.dp))
        PrimaryButton("Add idea") {
            if (title.isNotBlank()) {
                vm.addWishlist(
                    groupId,
                    WishlistCreateRequest(
                        title = title,
                        description = description.ifBlank { null },
                        product_url = url.ifBlank { null },
                        estimated_price = price.toDoubleOrNull(),
                        priority = "medium",
                        category = "other"
                    )
                )
                title = ""; description = ""; url = ""; price = ""
            }
        }
        LazyColumn(verticalArrangement = Arrangement.spacedBy(10.dp), modifier = Modifier.padding(top = 16.dp)) {
            items(state.wishlist, key = { it.id }) { item ->
                FestiveCard {
                    GoldChip(item.category)
                    Text(item.title, style = MaterialTheme.typography.titleLarge)
                    Text(item.description.orEmpty())
                    if (item.estimated_price != null) Text("About ${item.estimated_price}")
                }
            }
        }
    }
}
