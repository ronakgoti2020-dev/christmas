package com.secretsanta.app.data.local

import android.content.Context
import androidx.datastore.preferences.core.edit
import androidx.datastore.preferences.core.stringPreferencesKey
import androidx.datastore.preferences.preferencesDataStore
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.map

private val Context.dataStore by preferencesDataStore("secretsanta")

class TokenStore(private val context: Context) {
    private val tokenKey = stringPreferencesKey("access_token")
    private val apiKey = stringPreferencesKey("api_base_url")

    val token: Flow<String?> = context.dataStore.data.map { it[tokenKey] }
    val apiBaseUrl: Flow<String?> = context.dataStore.data.map { it[apiKey] }

    suspend fun saveToken(token: String) {
        context.dataStore.edit { it[tokenKey] = token }
    }

    suspend fun saveApiBaseUrl(url: String) {
        context.dataStore.edit { it[apiKey] = url }
    }

    suspend fun clear() {
        context.dataStore.edit { it.remove(tokenKey) }
    }
}
