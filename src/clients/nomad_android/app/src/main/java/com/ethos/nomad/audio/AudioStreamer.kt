// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.audio

import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.currentCoroutineContext
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.flow.flow
import kotlinx.coroutines.flow.flowOn
import kotlinx.coroutines.isActive

/**
 * AudioStreamer
 *
 * Captures raw 16kHz / 16-bit LE / Mono PCM audio from the device microphone
 * using [AudioRecord] and emits 100ms chunks (~3200 bytes) via a Kotlin [Flow].
 *
 * Wire format per chunk matches the mesh_protocol_v1 AudioChunkPayload contract:
 *   sample_rate_hz = 16000, channels = 1, bits_per_sample = 16
 *
 * Lifecycle:
 *   Call [start] to obtain the [Flow] and begin capture.
 *   Call [stop] to release the [AudioRecord] and terminate the flow.
 *
 * The flow runs on [Dispatchers.IO] internally; callers may collect on any dispatcher.
 *
 * Error handling:
 *   - [SecurityException]   → RECORD_AUDIO permission not granted. Flow terminates.
 *   - [IllegalStateException] → Microphone busy or AudioRecord init failed. Flow terminates.
 *   - [AudioRecord] read errors (negative return) → logged, chunk skipped, capture continues.
 */
class AudioStreamer {

    companion object {
        private const val TAG = "AudioStreamer"

        // ── Audio parameters ──────────────────────────────────────
        const val SAMPLE_RATE_HZ = 16_000
        const val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
        const val AUDIO_FORMAT   = AudioFormat.ENCODING_PCM_16BIT

        /** 100ms at 16kHz × 2 bytes/sample = 3200 bytes. */
        const val CHUNK_BYTES = 3_200

        /** Hard ceiling per AudioChunkPayload contract. */
        const val MAX_CHUNK_BYTES = 65_536
    }

    // ── State ─────────────────────────────────────────────────────
    @Volatile private var audioRecord: AudioRecord? = null
    @Volatile private var isCapturing = false

    // ── Public API ────────────────────────────────────────────────

    /**
     * Starts microphone capture and returns a [Flow] that emits raw PCM [ByteArray]s.
     *
     * Each emitted array is exactly [CHUNK_BYTES] bytes (~100ms of audio).
     * The flow is cold: capture only begins when the flow is collected.
     * Calling [stop] cancels the internal loop and completes the flow normally.
     *
     * @throws SecurityException if RECORD_AUDIO permission is missing.
     * @throws IllegalStateException if the microphone cannot be initialised.
     */
    fun start(): Flow<ByteArray> = flow {
        val minBuffer = AudioRecord.getMinBufferSize(SAMPLE_RATE_HZ, CHANNEL_CONFIG, AUDIO_FORMAT)
        if (minBuffer == AudioRecord.ERROR || minBuffer == AudioRecord.ERROR_BAD_VALUE) {
            throw IllegalStateException("AudioRecord.getMinBufferSize returned error: $minBuffer")
        }

        // Use at least CHUNK_BYTES or the system minimum, whichever is larger.
        val bufferSize = maxOf(minBuffer, CHUNK_BYTES * 2)

        val record = try {
            AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE_HZ,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize
            )
        } catch (e: SecurityException) {
            Log.e(TAG, "RECORD_AUDIO permission denied", e)
            throw e
        } catch (e: IllegalArgumentException) {
            Log.e(TAG, "AudioRecord init failed with bad arguments", e)
            throw IllegalStateException("AudioRecord cannot be initialised", e)
        }

        if (record.state != AudioRecord.STATE_INITIALIZED) {
            record.release()
            throw IllegalStateException("AudioRecord failed to initialise (microphone busy?)")
        }

        audioRecord = record

        try {
            record.startRecording()
            isCapturing = true
            Log.i(TAG, "Capture started — ${SAMPLE_RATE_HZ}Hz / 16-bit / Mono / ${CHUNK_BYTES}B chunks")

            val buffer = ByteArray(CHUNK_BYTES)

            // Read loop — runs until stop() is called or the coroutine is cancelled.
            while (isCapturing && currentCoroutineContext().isActive) {
                val bytesRead = record.read(buffer, 0, CHUNK_BYTES)

                when {
                    bytesRead == AudioRecord.ERROR_INVALID_OPERATION -> {
                        Log.e(TAG, "AudioRecord.read: ERROR_INVALID_OPERATION — stopping")
                        break
                    }
                    bytesRead == AudioRecord.ERROR_BAD_VALUE -> {
                        Log.e(TAG, "AudioRecord.read: ERROR_BAD_VALUE — stopping")
                        break
                    }
                    bytesRead < 0 -> {
                        Log.w(TAG, "AudioRecord.read returned $bytesRead — skipping chunk")
                        // Non-fatal: skip this chunk and keep going.
                        continue
                    }
                    bytesRead == 0 -> {
                        // Silence or very brief underrun — skip without logging spam.
                        continue
                    }
                    bytesRead > MAX_CHUNK_BYTES -> {
                        Log.w(TAG, "Chunk exceeds max size ($bytesRead > $MAX_CHUNK_BYTES) — skipping")
                        continue
                    }
                    else -> {
                        // Happy path: emit a defensive copy so the buffer can be reused.
                        emit(buffer.copyOf(bytesRead))
                    }
                }
            }
        } finally {
            isCapturing = false
            record.stop()
            record.release()
            audioRecord = null
            Log.i(TAG, "Capture stopped and AudioRecord released")
        }
    }.flowOn(Dispatchers.IO)

    /**
     * Signals the capture loop to terminate.
     *
     * The [Flow] returned by [start] will complete normally after the current
     * read() call returns (at most ~100ms delay). Safe to call from any thread.
     */
    fun stop() {
        if (isCapturing) {
            isCapturing = false
            Log.d(TAG, "stop() called — capture will halt after current read()")
        }
    }

    /**
     * Returns true if a capture session is currently active.
     */
    val isRunning: Boolean
        get() = isCapturing
}
