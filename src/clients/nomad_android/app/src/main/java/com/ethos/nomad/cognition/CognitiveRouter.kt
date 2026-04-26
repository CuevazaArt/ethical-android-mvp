package com.ethos.nomad.cognition

import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow

/**
 * Hybrid Cognitive Router
 * Decides whether to route a task to the On-Device SLM (Small Language Model)
 * or the Cloud LLM based on complexity, network availability, and privacy needs.
 */
class CognitiveRouter(
    private val localSlm: LocalModelClient,
    private val remoteLlm: CloudModelClient
) {

    enum class ProcessingTier {
        LOCAL_ONLY,
        CLOUD_PREFERRED,
        HYBRID_FALLBACK
    }

    /**
     * Estimates task complexity (0.0 to 1.0)
     * e.g., "Enciende la luz" -> 0.1
     * "Resume mi filosofía de vida basado en mis últimos 3 meses" -> 0.9
     */
    private fun estimateComplexity(prompt: String): Float {
        val wordCount = prompt.split(" ").size
        if (wordCount < 5 && isCommand(prompt)) return 0.1f
        if (prompt.contains("analiza") || prompt.contains("resume") || prompt.contains("filosofía")) return 0.8f
        return 0.5f // Default
    }

    private fun isCommand(prompt: String): Boolean {
        val p = prompt.lowercase()
        return p.startsWith("enciende") || p.startsWith("apaga") || p.startsWith("dime la hora")
    }

    private fun determineTier(prompt: String, isNetworkAvailable: Boolean): ProcessingTier {
        if (!isNetworkAvailable) return ProcessingTier.LOCAL_ONLY
        
        val complexity = estimateComplexity(prompt)
        
        // Fast response for simple commands / casual chat
        if (complexity < 0.3f) return ProcessingTier.LOCAL_ONLY
        
        // Deep reasoning goes to the cloud
        return ProcessingTier.CLOUD_PREFERRED
    }

    suspend fun process(prompt: String, isNetworkAvailable: Boolean): Flow<String> = flow {
        val tier = determineTier(prompt, isNetworkAvailable)

        when (tier) {
            ProcessingTier.LOCAL_ONLY -> {
                // Execute on local SLM (e.g. ExecuTorch / MediaPipe Llama 3 8B)
                localSlm.generateStream(prompt).collect { emit(it) }
            }
            ProcessingTier.CLOUD_PREFERRED -> {
                try {
                    // Try the cloud via WebSocket
                    remoteLlm.generateStream(prompt).collect { emit(it) }
                } catch (e: Exception) {
                    // Fallback to local if cloud times out or fails
                    emit("\n[Ethos Cloud no disponible, procesando localmente...]\n")
                    localSlm.generateStream(prompt).collect { emit(it) }
                }
            }
            ProcessingTier.HYBRID_FALLBACK -> {
                // Edge case: maybe use local to answer immediately while cloud thinks
                emit("[Analizando profundamente...]\n")
                remoteLlm.generateStream(prompt).collect { emit(it) }
            }
        }
    }
}

// Minimal Interfaces
interface LocalModelClient {
    suspend fun generateStream(prompt: String): Flow<String>
}

interface CloudModelClient {
    suspend fun generateStream(prompt: String): Flow<String>
}
