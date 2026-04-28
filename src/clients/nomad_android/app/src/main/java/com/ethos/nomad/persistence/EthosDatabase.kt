// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.persistence

import android.content.Context
import androidx.room.Database
import androidx.room.Room
import androidx.room.RoomDatabase
import com.ethos.nomad.persistence.daos.*
import com.ethos.nomad.persistence.entities.*

@Database(entities = [MemoryEntity::class, RosterEntity::class, IdentityEntity::class], version = 1, exportSchema = false)
abstract class EthosDatabase : RoomDatabase() {
    abstract fun memoryDao(): MemoryDao
    abstract fun rosterDao(): RosterDao
    abstract fun identityDao(): IdentityDao

    companion object {
        @Volatile
        private var INSTANCE: EthosDatabase? = null

        fun getDatabase(context: Context): EthosDatabase {
            return INSTANCE ?: synchronized(this) {
                val instance = Room.databaseBuilder(
                    context.applicationContext,
                    EthosDatabase::class.java,
                    "ethos_database"
                ).build()
                INSTANCE = instance
                instance
            }
        }
    }
}
