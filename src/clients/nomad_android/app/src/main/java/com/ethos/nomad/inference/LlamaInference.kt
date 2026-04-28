// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.inference

import android.util.Log

/**
 * LlamaInference — Wrapper for llama.cpp native library.
 * Fase 24b Integration.
 */
class LlamaInference {

    companion object {
        private const val TAG = "LlamaInference"

        init {
            try {
                System.loadLibrary("nomad_llama")
                Log.d(TAG, "Native library 'nomad_llama' loaded successfully.")
            } catch (e: UnsatisfiedLinkError) {
                Log.e(TAG, "Failed to load native library 'nomad_llama'", e)
            }
        }
    }

    /**
     * Native methods for real llama.cpp interaction.
     */
    external fun loadModel(modelPath: String): Boolean
    external fun generateResponse(prompt: String): String
    external fun unloadModel()

    /**
     * Higher level inference call.
     */
    fun generate(prompt: String): String {
        Log.d(TAG, "Inference requested for prompt: '${prompt.take(20)}...'")
        return generateResponse(prompt)
    }
}
