// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.inference

import android.content.Context
import android.util.Log
import com.ethos.nomad.core.HardwareProfiler

/**
 * HybridInference — Adaptive brain selector.
 * Switches between Cloud, LAN (Ollama), and Local (llama.cpp) based on context.
 */
class HybridInference(private val context: Context) {
    private val TAG = "HybridInference"
    private val client = OkHttpClient()
    private val hardwareProfiler = HardwareProfiler(context)
    private val llamaNative = LlamaInference()

    enum class BrainSource { CLOUD, OLLAMA, LOCAL }

    /**
     * Main entry point for generating a response.
     */
    suspend fun generateResponse(prompt: String, preferredSource: BrainSource = BrainSource.LOCAL): String {
        val specs = hardwareProfiler.getSpecs()
        Log.d(TAG, "Generating response. Tier: ${specs.recommendedTier}, Preferred: $preferredSource")

        return when (preferredSource) {
            BrainSource.CLOUD -> generateCloud(prompt)
            BrainSource.OLLAMA -> generateOllama(prompt)
            BrainSource.LOCAL -> generateLocal(prompt)
        }
    }

    private suspend fun generateLocal(prompt: String): String {
        Log.d(TAG, "Using Local Inerence (llama.cpp)")
        // Verify model is loaded, etc.
        return llamaNative.generate(prompt)
    }

    private fun generateOllama(prompt: String): String {
        Log.d(TAG, "Using LAN Inference (Ollama)")
        // Real implementation would call http://[LAN-IP]:11434/api/generate
        return "[OLLAMA MOCK] Response from local network server."
    }

    private fun generateCloud(prompt: String): String {
        Log.d(TAG, "Using Cloud Inference (Commercial API)")
        // Real implementation for Claude/OpenAI
        return "[CLOUD MOCK] Response from Anthropic/OpenAI."
    }
}
