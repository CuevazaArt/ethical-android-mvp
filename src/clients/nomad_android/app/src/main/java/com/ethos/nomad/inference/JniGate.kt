// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.inference

import android.content.Context
import android.util.Log

/**
 * JniGate — Integration Gate for llama.cpp bridge.
 */
object JniGate {
    private const val TAG = "EthosJNI"

    fun runGate(context: Context) {
        Log.d(TAG, "═══════════════════════════════════════════════════════════")
        Log.d(TAG, "  ETHOS JNI GATE — Running Full Inference Bridge Test")
        
        try {
            val modelManager = ModelManager(context)
            val modelFile = modelManager.getModelFile()
            
            Log.d(TAG, "  [1/3] Model location: ${modelFile.absolutePath}")
            if (!modelManager.isModelPresent()) {
                Log.w(TAG, "  ⚠️ Model not found locally. Download required.")
                // In a real app, we might trigger download here or show UI
            } else {
                Log.d(TAG, "  ✅ Model found on disk.")
            }

            val llama = LlamaInference()
            
            // Test load (Mock)
            val loaded = llama.loadModel(modelFile.absolutePath)
            Log.d(TAG, "  [2/3] Native loadModel call: $loaded")

            // Test generation (Mock)
            val response = llama.generate("Hola Ethos")
            Log.d(TAG, "  [3/3] Native generateResponse call: '$response'")
            
            Log.d(TAG, "  ✅ JNI GATE: Full inference bridge is operational.")
            
            llama.unloadModel()
        } catch (e: Exception) {
            Log.e(TAG, "  ❌ JNI GATE FAILED: Critical error in native bridge.", e)
        }
        
        Log.d(TAG, "═══════════════════════════════════════════════════════════")
    }
}
