// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.audio

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import java.util.Locale

/**
 * TtsEngine — Manages the vocal identity of Ethos.
 * Uses Android's native TTS engine (Google TTS).
 * Target: Transition to Sherpa-ONNX / Piper in Phase 25+.
 *
 * Language selection: prefers es-ES, falls back to en-US if Spanish
 * language data is missing (common in emulators without full TTS packs).
 */
class TtsEngine(context: Context) : TextToSpeech.OnInitListener {
    private val TAG = "EthosTTS"
    private var tts: TextToSpeech? = TextToSpeech(context, this)

    // @Volatile: isReady may be checked from the IO thread (wake-word callback)
    @Volatile private var isReady = false

    override fun onInit(status: Int) {
        if (status != TextToSpeech.SUCCESS) {
            Log.e(TAG, "TTS Initialization failed (status=$status).")
            return
        }
        // Prefer Spanish (es-ES); fall back to en-US for emulators
        val preferred = setLanguageSafe(Locale("es", "ES"))
        if (!preferred) {
            Log.w(TAG, "Spanish TTS not available — falling back to en-US.")
            setLanguageSafe(Locale.US)
        }
    }

    private fun setLanguageSafe(locale: Locale): Boolean {
        val result = tts?.setLanguage(locale)
        return when (result) {
            TextToSpeech.LANG_MISSING_DATA, TextToSpeech.LANG_NOT_SUPPORTED -> {
                Log.w(TAG, "Locale $locale not supported.")
                false
            }
            else -> {
                isReady = true
                Log.i(TAG, "TTS ready (locale: $locale).")
                true
            }
        }
    }

    /** Speak text. Safe to call from any thread. */
    fun speak(text: String) {
        if (!isReady) {
            Log.w(TAG, "TTS not ready — dropping: '${text.take(20)}'")
            return
        }
        if (text.isBlank()) return
        Log.d(TAG, "Speaking: ${text.take(40)}...")
        tts?.speak(text.trim(), TextToSpeech.QUEUE_FLUSH, null, "ethos_utterance")
    }

    /** Stop any ongoing speech immediately. */
    fun stop() {
        tts?.stop()
    }

    /** Shutdown the TTS engine and release resources. */
    fun release() {
        tts?.shutdown()
        tts = null
        isReady = false
    }
}
