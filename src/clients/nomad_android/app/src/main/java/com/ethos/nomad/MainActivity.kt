// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad

import android.content.Intent
import android.os.Bundle
import android.util.Log
import androidx.activity.ComponentActivity
import androidx.activity.compose.setContent
import androidx.compose.foundation.layout.fillMaxSize
import androidx.compose.material3.MaterialTheme
import androidx.compose.material3.Surface
import androidx.compose.ui.Modifier

import android.Manifest
import android.content.pm.PackageManager
import androidx.core.app.ActivityCompat
import androidx.core.content.ContextCompat
import com.ethos.nomad.core.EthosKernelGate
import com.ethos.nomad.inference.JniGate
import com.ethos.nomad.persistence.PersistenceGate
import com.ethos.nomad.ui.ChatScreen

class MainActivity : ComponentActivity() {
    private val TAG = "MainActivity"
    private val RECORD_AUDIO_REQUEST_CODE = 1001

    override fun onCreate(savedInstanceState: Bundle?) {
        super.onCreate(savedInstanceState)

        // ── Fase 24a: Ethos Kernel Integration Gate ──────────────────
        val gateResult = EthosKernelGate.runGate()
        Log.d(TAG, "Ethos Kernel Gate: ${gateResult.passed}/${gateResult.total} " +
                if (gateResult.allPassed) "✅ ALL PASSED" else "⚠️ ${gateResult.failed} FAILED")

        // ── Fase 24b: Persistence Gate (Room DB) ─────────────────────
        PersistenceGate.runGate(this)

        // ── Fase 24b: JNI Gate (llama.cpp) ───────────────────────────
        JniGate.runGate(this)

        checkPermissionsAndStartService()

        setContent {
            MaterialTheme {
                Surface(
                    modifier = Modifier.fillMaxSize(),
                    color = MaterialTheme.colorScheme.background
                ) {
                    ChatScreen()
                }
            }
        }
    }

    private fun checkPermissionsAndStartService() {
        if (ContextCompat.checkSelfPermission(this, Manifest.permission.RECORD_AUDIO) != PackageManager.PERMISSION_GRANTED) {
            ActivityCompat.requestPermissions(
                this,
                arrayOf(Manifest.permission.RECORD_AUDIO),
                RECORD_AUDIO_REQUEST_CODE
            )
        } else {
            startNomadService()
        }
    }

    override fun onRequestPermissionsResult(requestCode: Int, permissions: Array<out String>, grantResults: IntArray) {
        super.onRequestPermissionsResult(requestCode, permissions, grantResults)
        if (requestCode == RECORD_AUDIO_REQUEST_CODE && grantResults.isNotEmpty() && grantResults[0] == PackageManager.PERMISSION_GRANTED) {
            startNomadService()
        }
    }

    private fun startNomadService() {
        val serviceIntent = Intent(this, NomadService::class.java)
        if (android.os.Build.VERSION.SDK_INT >= android.os.Build.VERSION_CODES.O) {
            startForegroundService(serviceIntent)
        } else {
            startService(serviceIntent)
        }
    }
}

