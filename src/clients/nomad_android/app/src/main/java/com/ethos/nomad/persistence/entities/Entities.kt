// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.persistence.entities

import androidx.room.Entity
import androidx.room.PrimaryKey

@Entity(tableName = "memory")
data class MemoryEntity(
    @PrimaryKey(autoGenerate = true) val id: Long = 0,
    val timestamp: Long,
    val role: String, // "user" or "assistant"
    val content: String,
    val metadata: String? = null // JSON string for extended context
)

@Entity(tableName = "roster")
data class RosterEntity(
    @PrimaryKey val id: String, // Unique handle or ID
    val name: String,
    val summary: String,
    val lastSeen: Long
)

@Entity(tableName = "identity")
data class IdentityEntity(
    @PrimaryKey val key: String,
    val value: String
)
