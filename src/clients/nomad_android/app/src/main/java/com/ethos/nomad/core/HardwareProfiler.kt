// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.core

import android.app.ActivityManager
import android.content.Context
import android.util.Log

/**
 * HardwareProfiler — Analyzes device capabilities to choose the right model tier.
 */
class HardwareProfiler(private val context: Context) {
    private val TAG = "HardwareProfiler"

    data class DeviceSpecs(
        val totalRamGb: Int,
        val availableRamGb: Int,
        val recommendedTier: String
    )

    fun getSpecs(): DeviceSpecs {
        val actManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memInfo = ActivityManager.MemoryInfo()
        actManager.getMemoryInfo(memInfo)

        val totalRamGb = (memInfo.totalMem / (1024 * 1024 * 1024)).toInt()
        val availableRamGb = (memInfo.availMem / (1024 * 1024 * 1024)).toInt()

        val tier = when {
            totalRamGb >= 12 -> "CENTINELA"
            totalRamGb >= 8  -> "NOMAD"
            else             -> "POCKET"
        }

        Log.d(TAG, "Device Specs: RAM=${totalRamGb}GB (Avail=${availableRamGb}GB) -> Tier=$tier")
        return DeviceSpecs(totalRamGb, availableRamGb, tier)
    }
}
