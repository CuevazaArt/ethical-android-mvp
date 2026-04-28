// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.inference

import android.app.DownloadManager
import android.content.Context
import android.net.Uri
import android.util.Log
import java.io.File

import com.ethos.nomad.core.HardwareProfiler

/**
 * ModelManager — Handles GGUF model lifecycle with hardware awareness.
 */
class ModelManager(private val context: Context) {
    private val TAG = "ModelManager"
    private val hardwareProfiler = HardwareProfiler(context)
    
    // Model definitions tied to tiers
    data class ModelInfo(val name: String, val url: String, val minRamGb: Int)
    
    private val MODEL_ZOO = mapOf(
        "POCKET" to ModelInfo("llama-3.2-1b-instruct-q4_k_m.gguf", "https://huggingface.co/.../Llama-3.2-1B-Instruct-Q4_K_M.gguf", 4),
        "NOMAD" to ModelInfo("llama-3.2-3b-instruct-q4_k_m.gguf", "https://huggingface.co/.../Llama-3.2-3B-Instruct-Q4_K_M.gguf", 8),
        "CENTINELA" to ModelInfo("mistral-7b-v0.3-q4_k_m.gguf", "https://huggingface.co/.../Mistral-7B-v0.3.Q4_K_M.gguf", 12)
    )

    private fun getTargetModel(): ModelInfo {
        val tier = hardwareProfiler.getSpecs().recommendedTier
        return MODEL_ZOO[tier] ?: MODEL_ZOO["POCKET"]!!
    }

    private val MODEL_FILENAME get() = getTargetModel().name
    private val MODEL_URL get() = getTargetModel().url

    /**
     * Returns the local file for the model.
     */
    fun getModelFile(): File {
        return File(context.getExternalFilesDir(null), MODEL_FILENAME)
    }

    /**
     * Checks if the model is already downloaded.
     */
    fun isModelPresent(): Boolean {
        val file = getModelFile()
        val exists = file.exists() && file.length() > 100_000_000 // ~100MB minimum for 1B model
        Log.d(TAG, "Model present check: $exists (${file.absolutePath})")
        return exists
    }

    /**
     * Starts the download via Android DownloadManager.
     */
    fun downloadModel() {
        if (isModelPresent()) {
            Log.d(TAG, "Model already present, skipping download.")
            return
        }

        Log.d(TAG, "Starting model download from: $MODEL_URL")
        val request = DownloadManager.Request(Uri.parse(MODEL_URL))
            .setTitle("Ethos SLM Model")
            .setDescription("Downloading Llama 3.2 1B for local inference")
            .setNotificationVisibility(DownloadManager.Request.VISIBILITY_VISIBLE_NOTIFY_COMPLETED)
            .setDestinationInExternalFilesDir(context, null, MODEL_FILENAME)
            .setAllowedOverMetered(true)
            .setAllowedOverRoaming(true)

        val downloadManager = context.getSystemService(Context.DOWNLOAD_SERVICE) as DownloadManager
        downloadManager.enqueue(request)
    }
}
