// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.persistence

import android.content.Context
import android.util.Log
import com.ethos.nomad.persistence.entities.MemoryEntity
import com.ethos.nomad.ui.ChatMessage
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.withContext

/**
 * MemoryBridge — Connects ChatViewModel to Room persistence.
 * Converts between ChatMessage (UI) and MemoryEntity (DB).
 */
class MemoryBridge(context: Context) {
    private val TAG = "MemoryBridge"
    private val db = EthosDatabase.getDatabase(context)
    private val memoryDao = db.memoryDao()

    /**
     * Persist a chat message to the local database.
     */
    suspend fun save(message: ChatMessage) = withContext(Dispatchers.IO) {
        try {
            val entity = MemoryEntity(
                timestamp = message.timestamp,
                role = if (message.isUser) "user" else "assistant",
                content = message.text,
                metadata = message.ethicsContext
            )
            memoryDao.insert(entity)
        } catch (e: Exception) {
            Log.e(TAG, "Failed to persist message", e)
        }
    }

    /**
     * Load recent chat history from the database.
     * Returns messages in chronological order (oldest first).
     */
    suspend fun loadRecent(limit: Int = 50): List<ChatMessage> = withContext(Dispatchers.IO) {
        try {
            val entities = memoryDao.getRecent(limit)
            // getRecent returns DESC order, reverse to chronological
            entities.reversed().map { entity ->
                ChatMessage(
                    text = entity.content,
                    isUser = entity.role == "user",
                    ethicsContext = entity.metadata,
                    timestamp = entity.timestamp
                )
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to load history", e)
            emptyList()
        }
    }

    /**
     * Returns the total number of persisted messages.
     */
    suspend fun count(): Int = withContext(Dispatchers.IO) {
        try {
            memoryDao.count()
        } catch (e: Exception) {
            Log.e(TAG, "Failed to count memories", e)
            0
        }
    }
}
