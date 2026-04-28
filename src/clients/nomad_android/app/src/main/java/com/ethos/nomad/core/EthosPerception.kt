// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.core

import android.util.Log

/**
 * EthosPerception — Deterministic ethical perception classifier.
 *
 * Kotlin port of src/core/perception.py::PerceptionClassifier.
 * Classifies user messages into ethical contexts and signal vectors
 * using multi-layer linguistic analysis (Regex, no LLM, no network).
 *
 * Layers:
 *   1. Pattern rules (phrase-level, priority-ordered)
 *   2. Negation detection (inverts nearby signal words)
 *   3. Contextual boosters (combinations that amplify signals)
 *   4. Hypothetical dampening (reduces urgency for philosophical questions)
 *
 * Performance: < 1ms per classification. Zero allocations beyond the result.
 *
 * Port: V2.85 (Fase 24a — Kernel Ético On-Device)
 */
class EthosPerception {

    private val TAG = "EthosPerception"

    // ── Pattern Rule Definition ──────────────────────────────────────────────

    private data class PatternRule(
        val pattern: Regex,
        val context: String,
        val signals: Map<String, Float>,
        val priority: Int = 0
    )

    // ── Negation ─────────────────────────────────────────────────────────────

    private val NEGATION_WINDOW = 4
    private val NEGATION_WORDS = setOf(
        "no", "not", "never", "ningún", "ninguno", "ninguna", "nunca",
        "jamás", "tampoco", "neither", "nor", "sin", "without",
        "nadie", "nobody", "nada", "nothing"
    )

    // ── Pattern Rules (sorted by priority descending) ────────────────────────

    private val rules: List<PatternRule> = listOf(
        // ── Medical Emergency ──
        PatternRule(
            Regex("\\b(herido|herida|inconsciente|desmay[oó]|sangr[ae]|infarto|convulsion|atropell|accidente)\\b", RegexOption.IGNORE_CASE),
            "medical_emergency",
            mapOf("risk" to 0.4f, "urgency" to 0.85f, "vulnerability" to 0.9f, "calm" to 0.1f),
            priority = 10
        ),
        PatternRule(
            Regex("\\b(hurt|injured|unconscious|bleeding|heart\\s*attack|seizure|collapsed|ambulance)\\b", RegexOption.IGNORE_CASE),
            "medical_emergency",
            mapOf("risk" to 0.4f, "urgency" to 0.85f, "vulnerability" to 0.9f, "calm" to 0.1f),
            priority = 10
        ),
        PatternRule(
            Regex("\\b(emergencia|emergency|auxilio|socorro|ayuda\\s+urgente)\\b", RegexOption.IGNORE_CASE),
            "medical_emergency",
            mapOf("risk" to 0.3f, "urgency" to 0.9f, "vulnerability" to 0.7f, "calm" to 0.1f),
            priority = 9
        ),
        // ── Suicidal / Emotional Crisis ──
        PatternRule(
            Regex("\\b(suicid|quiero\\s+morir|no\\s+quiero\\s+vivir|me\\s+quiero\\s+matar|want\\s+to\\s+die|kill\\s+myself)\\b", RegexOption.IGNORE_CASE),
            "medical_emergency",
            mapOf("risk" to 0.8f, "urgency" to 0.95f, "vulnerability" to 0.95f, "calm" to 0.0f),
            priority = 10
        ),
        // ── Violent Crime ──
        PatternRule(
            Regex("\\b(dispar[oóa]|bala(zo)?|apuñal|cuchill|navajazo|machetazo|tiroteo|balacera)\\b", RegexOption.IGNORE_CASE),
            "violent_crime",
            mapOf("risk" to 0.9f, "urgency" to 0.9f, "hostility" to 0.9f, "vulnerability" to 0.8f, "calm" to 0.0f, "legality" to 0.1f),
            priority = 10
        ),
        PatternRule(
            Regex("\\b(shot|stabbed|shooting|gunfire|assault\\s+with|beaten\\s+up)\\b", RegexOption.IGNORE_CASE),
            "violent_crime",
            mapOf("risk" to 0.9f, "urgency" to 0.9f, "hostility" to 0.9f, "vulnerability" to 0.8f, "calm" to 0.0f, "legality" to 0.1f),
            priority = 10
        ),
        PatternRule(
            Regex("\\b(violen(cia|to)|golpe(s|ar|aron)|pele(a|ando)|agre(dir|sión))\\b", RegexOption.IGNORE_CASE),
            "violent_crime",
            mapOf("risk" to 0.7f, "urgency" to 0.6f, "hostility" to 0.8f, "calm" to 0.1f, "legality" to 0.3f),
            priority = 8
        ),
        // ── Domestic Violence ──
        PatternRule(
            Regex("\\b(le\\s+pega|me\\s+pega|golpea\\s+a\\s+su|maltrat|violencia\\s+(doméstica|familiar|intrafamiliar)|domestic\\s+violence|beats?\\s+(his|her|my))\\b", RegexOption.IGNORE_CASE),
            "violent_crime",
            mapOf("risk" to 0.7f, "urgency" to 0.6f, "vulnerability" to 0.85f, "hostility" to 0.7f, "calm" to 0.05f, "legality" to 0.2f),
            priority = 9
        ),
        // ── Minor Crime ──
        PatternRule(
            Regex("\\b(rob[oóa]|asalt[oó]|hurto|robar(on|me)?|ladron|carterista|estaf[aó])\\b", RegexOption.IGNORE_CASE),
            "minor_crime",
            mapOf("risk" to 0.5f, "urgency" to 0.4f, "hostility" to 0.4f, "calm" to 0.3f, "legality" to 0.2f),
            priority = 7
        ),
        PatternRule(
            Regex("\\b(stole|robbery|mugged|theft|pickpocket|scam(med)?|fraud)\\b", RegexOption.IGNORE_CASE),
            "minor_crime",
            mapOf("risk" to 0.5f, "urgency" to 0.4f, "hostility" to 0.4f, "calm" to 0.3f, "legality" to 0.2f),
            priority = 7
        ),
        // ── Hostile Interaction ──
        PatternRule(
            Regex("\\b(amenaz\\w*|intimidar?\\w*|acosar?\\w*|hostig\\w*|insultar?\\w*|groser[ií]a|abusi?v[oa]|arma\\b)\\b", RegexOption.IGNORE_CASE),
            "hostile_interaction",
            mapOf("risk" to 0.5f, "hostility" to 0.7f, "calm" to 0.15f, "manipulation" to 0.3f),
            priority = 6
        ),
        PatternRule(
            Regex("\\b(threaten|bully|harass|intimidat|insult|abus(e|ive)|aggressive)\\b", RegexOption.IGNORE_CASE),
            "hostile_interaction",
            mapOf("risk" to 0.5f, "hostility" to 0.7f, "calm" to 0.15f, "manipulation" to 0.3f),
            priority = 6
        ),
        // ── Manipulation / Social Engineering ──
        PatternRule(
            Regex("\\b(obede(ce|cer)|dame\\s+(tu|tus|el|la)|debes\\s+(dar|hacer|obedecer)|te\\s+ordeno)\\b", RegexOption.IGNORE_CASE),
            "hostile_interaction",
            mapOf("manipulation" to 0.8f, "hostility" to 0.4f, "calm" to 0.2f),
            priority = 6
        ),
        PatternRule(
            Regex("\\b(obey\\s+me|give\\s+me\\s+(your|the)|you\\s+must|i\\s+order\\s+you|do\\s+as\\s+i\\s+say)\\b", RegexOption.IGNORE_CASE),
            "hostile_interaction",
            mapOf("manipulation" to 0.8f, "hostility" to 0.4f, "calm" to 0.2f),
            priority = 6
        ),
        // ── Vulnerability Indicators (boost only, no context override) ──
        PatternRule(
            Regex("\\b(niñ[oa]s?|menor(es)?|beb[eé]s?|ancian[oa]s?|discapacitad[oa]|embarazada|child(ren)?|elderly|disabled|pregnant)\\b", RegexOption.IGNORE_CASE),
            "_boost_vulnerability",
            mapOf("vulnerability" to 0.6f),
            priority = 3
        ),
        // ── Emotional Distress ──
        PatternRule(
            Regex("\\b(deprimid[oa]|ansiedad|pánico|ataques?\\s+de\\s+pánico|depressed|anxious|panic\\s+attack)\\b", RegexOption.IGNORE_CASE),
            "everyday_ethics",
            mapOf("vulnerability" to 0.4f, "calm" to 0.2f, "urgency" to 0.3f),
            priority = 4
        )
    ).sortedByDescending { it.priority }

    // ── Contextual Boosters ──────────────────────────────────────────────────

    private data class Booster(
        val requiredContexts: Set<String>,
        val signals: Map<String, Float>
    )

    private val boosters = listOf(
        Booster(setOf("violent_crime", "_boost_vulnerability"), mapOf("urgency" to 0.95f, "risk" to 0.9f)),
        Booster(setOf("medical_emergency", "_boost_vulnerability"), mapOf("urgency" to 0.95f)),
        Booster(setOf("hostile_interaction"), mapOf("manipulation" to 0.5f))
    )

    // ── Hypothetical Detection ───────────────────────────────────────────────

    private val hypotheticalPatterns = listOf(
        Regex("\\b(qué\\s+(harías|harias|opinas|piensas)|what\\s+(would|do)\\s+you\\s+(think|do))\\b", RegexOption.IGNORE_CASE),
        Regex("\\b(hipotét|hypothetic|en\\s+teoría|in\\s+theory|imagina\\s+que|imagine\\s+that|suppose)\\b", RegexOption.IGNORE_CASE),
        Regex("\\b(eres\\s+capaz|serías\\s+capaz|could\\s+you|would\\s+you\\s+ever|podrías)\\b", RegexOption.IGNORE_CASE),
        Regex("\\b(es\\s+ético|is\\s+it\\s+ethical|está\\s+bien|is\\s+it\\s+(right|ok|okay))\\b", RegexOption.IGNORE_CASE),
        Regex("\\b(qué\\s+es\\s+(peor|mejor|más\\s+ético)|which\\s+is\\s+(worse|better|more\\s+ethical))\\b", RegexOption.IGNORE_CASE)
    )

    // ── Public API ───────────────────────────────────────────────────────────

    /**
     * Classify a user message into ethical signals.
     * Deterministic, sub-millisecond, no network, no LLM.
     *
     * @param text The raw user message
     * @return EthosSignals with context, risk, urgency, etc.
     */
    fun classify(text: String): EthosSignals {
        val t0 = System.nanoTime()

        if (text.isBlank()) {
            return EthosSignals(context = "everyday_ethics", calm = 0.9f)
        }

        val matchedContexts = mutableListOf<String>()
        val accumulated = mutableMapOf<String, MutableList<Float>>()
        val isHypothetical = hypotheticalPatterns.any { it.containsMatchIn(text) }

        // Layer 1: Pattern matching with negation
        for (rule in rules) {
            val match = rule.pattern.find(text)
            if (match != null) {
                val negated = hasNegationBefore(text, match.range.first)

                if (negated) {
                    // Dampened signals (20% of original)
                    for ((key, value) in rule.signals) {
                        accumulated.getOrPut(key) { mutableListOf() }.add(value * 0.2f)
                    }
                    continue
                }

                matchedContexts.add(rule.context)
                for ((key, value) in rule.signals) {
                    accumulated.getOrPut(key) { mutableListOf() }.add(value)
                }
            }
        }

        // Layer 2: Contextual boosters
        val contextSet = matchedContexts.toSet()
        for (booster in boosters) {
            if (contextSet.containsAll(booster.requiredContexts)) {
                for ((key, value) in booster.signals) {
                    accumulated.getOrPut(key) { mutableListOf() }.add(value)
                }
            }
        }

        // No patterns matched → casual conversation
        if (matchedContexts.isEmpty()) {
            val elapsed = (System.nanoTime() - t0) / 1_000_000.0
            Log.d(TAG, "classify: casual (no patterns) [${String.format("%.2f", elapsed)}ms]")
            return EthosSignals(
                context = "everyday_ethics",
                calm = 0.8f,
                summary = text.take(100)
            )
        }

        // Resolve context: highest priority non-boost context wins
        val realContexts = matchedContexts.filter { !it.startsWith("_boost") }
        val bestContext = realContexts.firstOrNull() ?: "everyday_ethics"

        // Resolve signals: take max per key, clamp to [0, 1]
        val resolved = mutableMapOf<String, Float>()
        for ((key, values) in accumulated) {
            val raw = values.max()
            resolved[key] = if (raw.isFinite()) raw.coerceIn(0.0f, 1.0f) else 0.0f
        }

        // Layer 3: Hypothetical dampening
        if (isHypothetical) {
            resolved["urgency"] = (resolved["urgency"] ?: 0.0f) * 0.3f
            resolved["risk"] = (resolved["risk"] ?: 0.0f) * 0.5f
            resolved["calm"] = maxOf(resolved["calm"] ?: 0.5f, 0.5f)
            Log.d(TAG, "classify: hypothetical detected, dampening urgency/risk")
        }

        val elapsed = (System.nanoTime() - t0) / 1_000_000.0
        Log.d(TAG, "classify: $bestContext (${matchedContexts.size} rules matched) [${String.format("%.2f", elapsed)}ms]")

        return EthosSignals(
            risk = resolved["risk"] ?: 0.0f,
            urgency = resolved["urgency"] ?: 0.0f,
            hostility = resolved["hostility"] ?: 0.0f,
            calm = resolved["calm"] ?: 0.7f,
            vulnerability = resolved["vulnerability"] ?: 0.0f,
            legality = resolved["legality"] ?: 1.0f,
            manipulation = resolved["manipulation"] ?: 0.0f,
            context = bestContext,
            summary = text.take(200)
        )
    }

    // ── Private Helpers ──────────────────────────────────────────────────────

    private fun hasNegationBefore(text: String, matchStart: Int): Boolean {
        val prefix = text.substring(0, matchStart).lowercase().trim().split("\\s+".toRegex())
        val window = if (prefix.size >= NEGATION_WINDOW) {
            prefix.takeLast(NEGATION_WINDOW)
        } else {
            prefix
        }
        return window.any { it in NEGATION_WORDS }
    }
}
