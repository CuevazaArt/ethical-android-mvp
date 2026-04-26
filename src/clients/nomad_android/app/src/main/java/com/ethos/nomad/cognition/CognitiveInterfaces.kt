// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.cognition

import kotlinx.coroutines.flow.Flow

// ─────────────────────────────────────────────────────────────
// CognitiveInterfaces.kt
//
// Architectural contract for the Hybrid Cognitive Router.
// Defines sealed hierarchies for routing decisions, sensory
// telemetry, and the interface boundaries between the on-device
// SLM (spinal reflexes) and the cloud Ethos Kernel (cortex).
//
// These interfaces are the ONLY coupling point between
// NomadService (Android lifecycle) and CognitiveRouter (logic).
// Implementations are injected, never hard-wired.
// ─────────────────────────────────────────────────────────────

// ── Processing Tier ─────────────────────────────────────────
// The routing decision is not a simple enum anymore.
// Each tier carries the metadata that led to the decision,
// enabling observability and future self-tuning.

sealed class ProcessingTier {

    /** Resolved entirely on-device. Zero network traffic. */
    data class Local(
        val reason: LocalReason
    ) : ProcessingTier()

    /** Delegated to the Ethos Kernel via WebSocket. */
    data class Cloud(
        val complexity: Float,
        val requiresMemory: Boolean
    ) : ProcessingTier()

    /**
     * Local answers immediately (spinal reflex) while the cloud
     * processes in parallel. The cloud response replaces the local
     * one when it arrives — or is discarded if the user interrupts.
     */
    data class HybridRace(
        val localEstimatedLatencyMs: Long,
        val cloudTimeoutMs: Long
    ) : ProcessingTier()
}

/** Why a prompt was routed locally. */
enum class LocalReason {
    /** Network is unavailable. No choice. */
    OFFLINE,
    /** Complexity below threshold. Faster locally. */
    LOW_COMPLEXITY,
    /** User explicitly requested private/offline mode. */
    PRIVACY_REQUESTED,
    /** The prompt matches a known device command (flashlight, alarm, etc). */
    DEVICE_COMMAND
}

// ── Cognitive Request ───────────────────────────────────────
// A unified envelope for everything the router receives.
// Comes from NomadService after STT or typed input.

data class CognitiveRequest(
    /** The transcribed or typed user text. */
    val text: String,
    /** Current network reachability. */
    val networkState: NetworkState,
    /** Ambient sensor snapshot at the moment of the request. */
    val sensorSnapshot: SensorSnapshot? = null,
    /** If true, the user explicitly toggled "offline mode" in the UI. */
    val forceLocal: Boolean = false
)

// ── Cognitive Response ──────────────────────────────────────
// Sealed hierarchy so consumers can pattern-match exhaustively.

sealed class CognitiveResponse {

    /** A streaming text response (token by token). */
    data class TextStream(
        val tokens: Flow<String>,
        val tier: ProcessingTier
    ) : CognitiveResponse()

    /** A device-level action (no LLM needed). */
    data class DeviceAction(
        val action: DeviceActionType,
        val confirmationText: String
    ) : CognitiveResponse()

    /** The system could not process the request at all. */
    data class Failure(
        val error: Throwable,
        val fallbackMessage: String
    ) : CognitiveResponse()
}

/** Actions that the Nómada can execute locally without any LLM. */
enum class DeviceActionType {
    TOGGLE_FLASHLIGHT,
    SET_ALARM,
    OPEN_APP,
    READ_BATTERY,
    READ_TIME,
    TAKE_PHOTO,
    NAVIGATE_MAP
}

// ── Network State ───────────────────────────────────────────

enum class NetworkState {
    /** Full connectivity (Wi-Fi or mobile data). */
    CONNECTED,
    /** Connected but metered (conserve bandwidth). */
    METERED,
    /** No network at all. */
    OFFLINE
}

// ── Sensor Snapshot ─────────────────────────────────────────
// A point-in-time reading of all available hardware sensors.
// Passed to the router so it can enrich context or detect
// environmental anomalies before routing.

data class SensorSnapshot(
    val batteryPercent: Int,
    val isCharging: Boolean,
    val ambientLightLux: Float? = null,
    val accelerometerMagnitude: Float? = null,
    val gpsLatitude: Double? = null,
    val gpsLongitude: Double? = null
)

// ── Core Interfaces ─────────────────────────────────────────
// These are the two "plugs" that CognitiveRouter depends on.
// In tests, both are mocked. In production:
//   - LocalModelClient → ExecuTorch / MediaPipe LLM Inference
//   - CloudModelClient → OkHttp WebSocket to Ethos Kernel

/**
 * Contract for the on-device Small Language Model.
 * Implementations must be non-blocking and stream tokens.
 */
interface LocalModelClient {
    /** Returns true if the local model is loaded and ready. */
    suspend fun isReady(): Boolean

    /** Stream tokens for a given prompt. Must not throw on empty input. */
    suspend fun generateStream(prompt: String): Flow<String>

    /** Estimated VRAM/RAM usage in MB. Used for thermal throttling decisions. */
    fun estimatedMemoryMb(): Int
}

/**
 * Contract for the remote Ethos Kernel connection.
 * Wraps the OkHttp WebSocket and speaks the Ethos JSON protocol.
 */
interface CloudModelClient {
    /** True if the WebSocket is currently open and authenticated. */
    fun isConnected(): Boolean

    /** Stream tokens from the Ethos Kernel for a given prompt. */
    suspend fun generateStream(prompt: String): Flow<String>

    /** Send a raw telemetry frame (sensor data, heartbeat, etc). */
    suspend fun sendTelemetry(payload: Map<String, Any>)
}

// ── Complexity Estimator ────────────────────────────────────
// Extracted as an interface so we can swap heuristic-based
// estimation for a learned classifier later.

/**
 * Estimates the cognitive complexity of a user prompt.
 * Returns a value in [0.0, 1.0] where:
 *   0.0 = trivial device command ("what time is it")
 *   1.0 = deep ethical reasoning ("should I forgive my father")
 */
interface ComplexityEstimator {
    fun estimate(text: String): Float
}

// ── Router Interface ────────────────────────────────────────
// The top-level contract. NomadService depends only on this.

/**
 * The Cognitive Router receives a [CognitiveRequest] and returns
 * a [CognitiveResponse]. It is the single decision point that
 * determines whether cognition happens locally or remotely.
 *
 * Implementations must:
 * 1. Never block the main thread.
 * 2. Always return a response (even if it's a Failure).
 * 3. Respect [CognitiveRequest.forceLocal] unconditionally.
 */
interface CognitiveRouterContract {
    suspend fun route(request: CognitiveRequest): CognitiveResponse
}
