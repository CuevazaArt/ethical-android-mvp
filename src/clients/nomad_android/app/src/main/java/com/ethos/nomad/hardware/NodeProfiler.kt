// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.hardware

import android.app.ActivityManager
import android.content.Context
import android.content.Intent
import android.content.IntentFilter
import android.os.BatteryManager
import java.io.File

/**
 * TelemetryData captures the hardware state of the Android node.
 */
data class TelemetryData(
    val batteryLevel: Float,
    val isCharging: Boolean,
    val batteryTemperatureC: Float?,
    val availableRamMb: Long,
    val totalRamMb: Long,
    val cpuTemperatureC: Float?
)

/**
 * NodeProfiler handles the collection of hardware metrics from the Android system.
 */
class NodeProfiler {

    /**
     * Captures a snapshot of the current hardware status.
     */
    fun snapshot(context: Context): TelemetryData {
        // 1. Battery Information
        val batteryIntent = context.registerReceiver(null, IntentFilter(Intent.ACTION_BATTERY_CHANGED))
        
        val level = batteryIntent?.getIntExtra(BatteryManager.EXTRA_LEVEL, -1) ?: -1
        val scale = batteryIntent?.getIntExtra(BatteryManager.EXTRA_SCALE, -1) ?: -1
        val batteryLevel = if (level != -1 && scale != -1) level / scale.toFloat() else 0f
        
        val status = batteryIntent?.getIntExtra(BatteryManager.EXTRA_STATUS, -1) ?: -1
        val isCharging = status == BatteryManager.BATTERY_STATUS_CHARGING || 
                         status == BatteryManager.BATTERY_STATUS_FULL
                         
        val batteryTempRaw = batteryIntent?.getIntExtra(BatteryManager.EXTRA_TEMPERATURE, -1) ?: -1
        val batteryTemperatureC = if (batteryTempRaw != -1) batteryTempRaw / 10.0f else null

        // 2. RAM Information
        val activityManager = context.getSystemService(Context.ACTIVITY_SERVICE) as ActivityManager
        val memoryInfo = ActivityManager.MemoryInfo()
        activityManager.getMemoryInfo(memoryInfo)
        val availableRamMb = memoryInfo.availMem / (1024 * 1024)
        val totalRamMb = memoryInfo.totalMem / (1024 * 1024)

        // 3. CPU Temperature
        val cpuTemperatureC = readCpuTemperature()

        return TelemetryData(
            batteryLevel = batteryLevel,
            isCharging = isCharging,
            batteryTemperatureC = batteryTemperatureC,
            availableRamMb = availableRamMb,
            totalRamMb = totalRamMb,
            cpuTemperatureC = cpuTemperatureC
        )
    }

    /**
     * Reads CPU temperature from the thermal zone system file.
     */
    private fun readCpuTemperature(): Float? {
        return try {
            val tempFile = File("/sys/class/thermal/thermal_zone0/temp")
            if (tempFile.exists()) {
                val tempText = tempFile.readText().trim()
                tempText.toFloat() / 1000f
            } else {
                null
            }
        } catch (e: Exception) {
            null
        }
    }
}
