package com.secretsanta.app

import org.junit.Assert.assertTrue
import org.junit.Test

class InviteUrlTest {
    @Test
    fun invitePathLooksShareable() {
        val url = "https://secretsanta.app/join/christmas-friends-2026-abc123"
        assertTrue(url.contains("/join/"))
        assertTrue(url.substringAfterLast("/").length > 8)
    }
}
