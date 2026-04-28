// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.persistence.daos

import androidx.room.*
import com.ethos.nomad.persistence.entities.*

@Dao
interface MemoryDao {
    @Insert
    suspend fun insert(memory: MemoryEntity)

    @Query("SELECT * FROM memory ORDER BY timestamp DESC LIMIT :limit")
    suspend fun getRecent(limit: Int = 50): List<MemoryEntity>

    @Query("SELECT * FROM memory ORDER BY timestamp DESC")
    suspend fun getAll(): List<MemoryEntity>

    @Query("SELECT COUNT(*) FROM memory")
    suspend fun count(): Int

    @Query("DELETE FROM memory")
    suspend fun deleteAll()
}

@Dao
interface RosterDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(roster: RosterEntity)

    @Query("SELECT * FROM roster")
    suspend fun getAll(): List<RosterEntity>
}

@Dao
interface IdentityDao {
    @Insert(onConflict = OnConflictStrategy.REPLACE)
    suspend fun insert(identity: IdentityEntity)

    @Query("SELECT value FROM identity WHERE `key` = :key")
    suspend fun getValue(key: String): String?
}
