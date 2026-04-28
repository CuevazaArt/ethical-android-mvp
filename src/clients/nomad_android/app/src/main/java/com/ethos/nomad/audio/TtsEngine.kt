// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.audio

import android.content.Context
import android.speech.tts.TextToSpeech
import android.util.Log
import java.util.Locale

/**
 * TtsEngine — Manages the vocal identity of Ethos.
 * Currently uses Android's native TTS engine.
 * Target: Transition to Sherpa-ONNX / Piper in Phase 25+.
 */
class TtsEngine(context: Context) : TextToSpeech.OnInitListener {
    private val TAG = "EthosTTS"
    private var tts: TextToSpeech? = TextToSpeech(context, this)
    private var isReady = false

    override fun onInit(status: Int) {
        if (status == TextToSpeech.SUCCESS) {
            val result = tts?.setLanguage(Locale("es", "ES"))
            if (result == TextToSpeech.LANG_MISSING_DATA || result == TextToSpeech.LANG_NOT_SUPPORTED) {
                Log.e(TAG, "Spanish language not supported or missing data")
            } else {
                isReady = true
                Log.i(TAG, "TTS Engine Initialized and Ready (Spanish).")
            }
        } else {
            Log.e(TAG, "TTS Initialization failed.")
        }
    }

    /**
     * Convert text to audible speech.
     */
    fun speak(text: String) {
        if (isReady && text.isNotEmpty()) {
            Log.d(TAG, "Speaking: ${text.take(30)}...")
            tts?.speak(text, TextToSpeech.QUEUE_FLUSH, null, "ethos_utterance")
        } else {
            Log.w(TAG, "TTS requested but engine not ready or text empty.")
        }
    }

    /**
     * Stop any ongoing speech.
     */
    fun stop() {
        tts?.stop()
    }

    /**
     * Release resources.
     */
    fun release() {
        tts?.shutdown()
        tts = null
    }
}
