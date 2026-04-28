// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.persistence

import android.content.Context
import android.util.Log
import com.ethos.nomad.persistence.entities.MemoryEntity
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext

/**
 * PersistenceGate — Integration Gate for Room DB.
 * Verifies that we can write and read from the local database.
 */
object PersistenceGate {
    private const val TAG = "EthosPersistence"

    fun runGate(context: Context) {
        val db = EthosDatabase.getDatabase(context)
        val memoryDao = db.memoryDao()

        CoroutineScope(Dispatchers.IO).launch {
            try {
                Log.d(TAG, "═══════════════════════════════════════════════════════════")
                Log.d(TAG, "  ETHOS PERSISTENCE GATE — Running Database Test")
                
                // 1. Clear previous test data (optional, but good for deterministic gate)
                memoryDao.deleteAll()
                
                // 2. Insert test memory
                val testContent = "Hola Ethos, soy Juan"
                val memory = MemoryEntity(
                    timestamp = System.currentTimeMillis(),
                    role = "user",
                    content = testContent
                )
                memoryDao.insert(memory)
                Log.d(TAG, "   [1/2] Memory saved: '$testContent'")

                // 3. Retrieve and verify
                val allMemories = memoryDao.getAll()
                if (allMemories.isNotEmpty() && allMemories[0].content == testContent) {
                    Log.d(TAG, "   [2/2] Memory retrieved correctly.")
                    Log.d(TAG, "  ✅ PERSISTENCE GATE: Memory saved and retrieved: '${allMemories[0].content}'")
                } else {
                    Log.e(TAG, "  ❌ PERSISTENCE GATE FAILED: Retrieval mismatch or empty list.")
                }
                Log.d(TAG, "═══════════════════════════════════════════════════════════")
            } catch (e: Exception) {
                Log.e(TAG, "  ❌ PERSISTENCE GATE CRITICAL ERROR", e)
            }
        }
    }
}
