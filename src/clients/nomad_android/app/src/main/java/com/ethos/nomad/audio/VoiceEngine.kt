// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.audio

import android.annotation.SuppressLint
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import kotlin.math.abs

/**
 * VoiceEngine — Manages continuous audio capture and silence detection (VAD).
 * Scaffolding for Sherpa-ONNX Wake Word integration.
 */
class VoiceEngine {
    private val TAG = "EthosVoice"
    private val SAMPLE_RATE = 16000
    private val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
    private val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT
    
    private var audioRecord: AudioRecord? = null
    private var isListening = false
    private var recordingJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO)

    /**
     * Start capturing audio from the microphone.
     */
    @SuppressLint("MissingPermission")
    fun startListening() {
        if (isListening) return

        val bufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)
        if (bufferSize == AudioRecord.ERROR_BAD_VALUE) {
            Log.e(TAG, "Invalid audio parameters.")
            return
        }

        try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord initialization failed.")
                return
            }

            audioRecord?.startRecording()
            isListening = true
            Log.i(TAG, "VoiceEngine: Continuous listening started.")

            recordingJob = scope.launch {
                val buffer = ShortArray(bufferSize)
                while (isListening) {
                    val read = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    if (read > 0) {
                        processAudio(buffer, read)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start VoiceEngine", e)
        }
    }

    /**
     * Process captured audio samples.
     * Currently: Simple RMS detection (VAD placeholder).
     */
    private fun processAudio(buffer: ShortArray, size: Int) {
        var sum = 0L
        for (i in 0 until size) {
            sum += abs(buffer[i].toInt())
        }
        val average = sum / size
        
        // Simple log for "sound detected" above threshold
        if (average > 1500) { // Arbitrary threshold for POC
            Log.v(TAG, "Sound detected (RMS: $average)")
            // Future: Feed to Sherpa-ONNX here
        }
    }

    /**
     * Stop capturing audio.
     */
    fun stopListening() {
        isListening = false
        recordingJob?.cancel()
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        Log.i(TAG, "VoiceEngine: Listening stopped.")
    }
}
