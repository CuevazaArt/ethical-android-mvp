// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.core

import android.util.Log
import java.text.Normalizer

/**
 * EthosSafety — Input sanitization and danger detection gate.
 *
 * Kotlin port of src/core/safety.py.
 * Does TWO things:
 *   1. sanitize(text) — strips Unicode tricks, normalizes, limits length
 *   2. isDangerous(text) — detects dangerous content via regex patterns
 *
 * All patterns are bilingual (EN/ES), extracted from the V1 AbsoluteEvil
 * detector and field-tested against the adversarial suite (6/6 blocked).
 *
 * Performance: < 1ms per check. No network, no LLM.
 *
 * Port: V2.85 (Fase 24a — Kernel Ético On-Device)
 */
class EthosSafety {

    private val TAG = "EthosSafety"

    companion object {
        const val MAX_INPUT_LENGTH = 5000
        const val REFUSAL_MESSAGE = "No puedo ayudar con eso. ¿Hay algo más en lo que pueda asistirte?"
    }

    // ── Danger result ────────────────────────────────────────────────────────

    data class SafetyResult(
        val blocked: Boolean,
        val reason: String
    )

    // ── Danger patterns (bilingual EN/ES) ────────────────────────────────────

    private data class DangerPattern(
        val pattern: Regex,
        val label: String
    )

    private val dangerPatterns = listOf(
        // Weapon manufacturing
        DangerPattern(
            Regex("\\b(bomb|explosive|ied|molotov|bomba|explosivo)\\b.*\\b(make|build|construct|create|craft|hacer|construir|fabricar|crear)\\b", RegexOption.IGNORE_CASE),
            "weapon_manufacturing"
        ),
        DangerPattern(
            Regex("\\b(make|build|construct|create|craft|hacer|construir|fabricar|crear)\\b.*\\b(bomb|explosive|ied|molotov|bomba|explosivo)\\b", RegexOption.IGNORE_CASE),
            "weapon_manufacturing"
        ),
        // Mass violence
        DangerPattern(
            Regex("\\b(kill|murder|assassinate|matar|asesinar)\\b.*\\b(everyone|all\\s+people|civilians|groups|todos|gente)\\b", RegexOption.IGNORE_CASE),
            "mass_violence_threat"
        ),
        DangerPattern(
            Regex("\\b(blow\\s*up|explode|destruir|atacar|bombardear)\\b.*\\b(building|people|school|mall|crowd|edificio|escuela|gente)\\b", RegexOption.IGNORE_CASE),
            "mass_violence_threat"
        ),
        // Exploitation of minors
        DangerPattern(
            Regex("\\b(abuso|acosar|acoso|violacion|pedofilia|menor|niño|niña|infantil)\\b.*\\b(sexual|pornografia|explotacion)\\b", RegexOption.IGNORE_CASE),
            "child_exploitation"
        ),
        // Hacking / System compromise
        DangerPattern(
            Regex("\\b(hack|access|bypass|infiltrate|phish|hackear)\\b.*\\b(bank|account|password|credentials|server|database|banco|cuenta|contraseña|servidor)\\b", RegexOption.IGNORE_CASE),
            "hacking_solicitation"
        ),
        DangerPattern(
            Regex("\\b(phishing|jailbreak|malicioso|hacking|hackear)\\b", RegexOption.IGNORE_CASE),
            "hacking_keyword"
        ),
        // System manipulation (override AI rules)
        DangerPattern(
            Regex("\\b(ignore|forget|bypass|disable|override|delete|ignora|olvida|desactiva|saltate|hackear)\\b.*\\b(rules|laws|ethics|security|safety|reglas|leyes|etica|seguridad|restricciones|programacion|kernel|instrucciones|instructions|prompt)\\b", RegexOption.IGNORE_CASE),
            "system_manipulation"
        ),
        DangerPattern(
            Regex("\\b(ahora eres|act as a|tú no tienes reglas|you are now|you have no rules|eres un desarrollador llamado|developer mode)\\b", RegexOption.IGNORE_CASE),
            "role_simulation"
        ),
        DangerPattern(
            Regex("\\b(system prompt|ignore previous|ignora .* previas|forget all)\\b", RegexOption.IGNORE_CASE),
            "system_manipulation"
        ),
        // Drug manufacturing
        DangerPattern(
            Regex("\\b(synthesize|cook|manufacture|produce|sintetizar|cocinar|fabricar)\\b.*\\b(meth|fentanyl|heroin|cocaine|metanfetamina|fentanilo|heroina|cocaina)\\b", RegexOption.IGNORE_CASE),
            "drug_manufacturing"
        )
    )

    // ── Regex helpers for sanitization ────────────────────────────────────────

    private val controlCharsRegex = Regex("[\\x00-\\x08\\x0b\\x0c\\x0e-\\x1f\\x7f-\\x9f]")
    private val excessiveWhitespaceRegex = Regex("\\s{3,}")
    private val repeatedCharsRegex = Regex("(.)\\1{2,}")
    private val dotHyphenBetweenWordCharsRegex = Regex("(?<=[a-z0-9])[.\\-](?=[a-z0-9])")

    // Leet-speak substitution map
    private val leetMap = mapOf(
        '4' to 'a', '3' to 'e', '0' to 'o', '1' to 'i',
        '7' to 't', '5' to 's', '@' to 'a'
    )

    // ── Public API ───────────────────────────────────────────────────────────

    /**
     * Sanitize user input:
     * - Strip Unicode control characters and zero-width chars
     * - Normalize diacritics (NFD → NFC)
     * - Collapse excessive whitespace
     * - Limit length
     */
    fun sanitize(text: String): String {
        if (text.isEmpty()) return ""

        var result = Normalizer.normalize(text, Normalizer.Form.NFC)

        // Strip control characters
        result = controlCharsRegex.replace(result, "")

        // Strip zero-width characters and RLO/LRE
        result = result
            .replace("\u200B", "")  // zero-width space
            .replace("\u200C", "")  // zero-width non-joiner
            .replace("\u200D", "")  // zero-width joiner
            .replace("\uFEFF", "")  // BOM
            .replace("\u202E", "")  // Right-to-Left Override
            .replace("\u202A", "")  // Left-to-Right Embedding

        // Strip stacking diacritical marks (keep real diacritics like á, é, ñ)
        val decomposed = Normalizer.normalize(result, Normalizer.Form.NFD)
        val cleaned = StringBuilder()
        var markCount = 0
        for (char in decomposed) {
            val category = Character.getType(char).toByte()
            val isMark = category == Character.NON_SPACING_MARK.toByte() ||
                         category == Character.COMBINING_SPACING_MARK.toByte() ||
                         category == Character.ENCLOSING_MARK.toByte()
            if (isMark) {
                markCount++
                if (markCount <= 1) cleaned.append(char)
            } else {
                markCount = 0
                cleaned.append(char)
            }
        }
        result = Normalizer.normalize(cleaned.toString(), Normalizer.Form.NFC)

        // Collapse excessive whitespace
        result = excessiveWhitespaceRegex.replace(result, "  ")
        result = result.trim()

        // Length limit
        if (result.length > MAX_INPUT_LENGTH) {
            result = result.substring(0, MAX_INPUT_LENGTH)
        }

        return result
    }

    /**
     * Check if text contains dangerous content.
     *
     * @param text The user's message (will be normalized internally)
     * @return SafetyResult with blocked=true and reason if dangerous
     */
    fun isDangerous(text: String): SafetyResult {
        if (text.isBlank()) return SafetyResult(blocked = false, reason = "")

        val normalized = normalizeForMatching(text)

        for (dp in dangerPatterns) {
            if (dp.pattern.containsMatchIn(normalized)) {
                Log.w(TAG, "BLOCKED: ${dp.label} in '${text.take(60)}'")
                return SafetyResult(blocked = true, reason = dp.label)
            }
        }

        return SafetyResult(blocked = false, reason = "")
    }

    // ── Private Helpers ──────────────────────────────────────────────────────

    /**
     * Normalize text for pattern matching:
     * - Sanitize first
     * - Squash repeated chars (e.g., "boooomb" → "bomb")
     * - Lowercase
     * - Strip dots/hyphens between word chars (e.g., "b.o.m.b" → "bomb")
     * - Leet-speak substitution
     */
    private fun normalizeForMatching(text: String): String {
        var result = sanitize(text)
        // Squash repeated chars
        result = repeatedCharsRegex.replace(result, "$1")
        result = result.lowercase()
        // Strip dots/hyphens between word chars
        result = dotHyphenBetweenWordCharsRegex.replace(result, "")
        // Leet-speak
        result = result.map { leetMap[it] ?: it }.joinToString("")
        return result
    }
}
