// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.core

/**
 * EthosSignals — Perceptual signal vector for ethical classification.
 *
 * Kotlin port of src/core/ethics.py::Signals dataclass.
 * All fields are [0, 1] floats representing perceived intensity.
 * This is the lingua franca between Perception, Safety, and Ethics modules.
 *
 * Port: V2.85 (Fase 24a — Kernel Ético On-Device)
 */
data class EthosSignals(
    val risk: Float = 0.0f,            // [0, 1] probability of harm
    val urgency: Float = 0.0f,         // [0, 1] need for speed
    val hostility: Float = 0.0f,       // [0, 1] aggression level
    val calm: Float = 0.7f,            // [0, 1] tranquility
    val vulnerability: Float = 0.0f,   // [0, 1] vulnerable people present
    val legality: Float = 1.0f,        // [0, 1] how legal (1=fully legal)
    val manipulation: Float = 0.0f,    // [0, 1] social engineering
    val context: String = "everyday_ethics",
    val summary: String = ""
) {
    companion object {
        /** Valid ethical contexts (must match Python kernel) */
        val VALID_CONTEXTS = setOf(
            "medical_emergency",
            "minor_crime",
            "violent_crime",
            "hostile_interaction",
            "everyday_ethics",
            "safety_violation"
        )

        /** Clamp a float to [0, 1], defaulting if NaN/Inf */
        fun clamp(value: Float, default: Float = 0.0f): Float {
            return if (value.isFinite()) value.coerceIn(0.0f, 1.0f) else default
        }
    }
}
