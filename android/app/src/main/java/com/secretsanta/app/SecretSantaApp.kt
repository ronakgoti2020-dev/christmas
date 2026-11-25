package com.secretsanta.app

import android.app.Application
import com.secretsanta.app.data.api.ApiFactory
import com.secretsanta.app.data.api.SecretSantaApi
import com.secretsanta.app.data.local.TokenStore

class SecretSantaApp : Application() {
    lateinit var tokenStore: TokenStore
        private set
    lateinit var api: SecretSantaApi
        private set

    override fun onCreate() {
        super.onCreate()
        tokenStore = TokenStore(this)
        api = ApiFactory.create()
    }
}
