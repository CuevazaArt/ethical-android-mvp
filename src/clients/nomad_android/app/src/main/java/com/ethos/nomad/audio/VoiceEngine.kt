// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.audio

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import com.k2fsa.sherpa.onnx.KeywordSpotter
import com.k2fsa.sherpa.onnx.KeywordSpotterConfig
import com.k2fsa.sherpa.onnx.OnlineModelConfig
import com.k2fsa.sherpa.onnx.OnlineTransducerModelConfig
import com.k2fsa.sherpa.onnx.FeatureConfig
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.launch
import java.io.File

/**
 * VoiceEngine — Continuous audio capture + Sherpa-ONNX Wake Word detection.
 *
 * Architecture:
 *   AudioRecord (16kHz PCM) -> Sherpa-ONNX KeywordSpotter -> onKeywordDetected callback
 *
 * Model: Zipformer wenetspeech 3.3M, ~26MB
 * Keywords: ["ethos", "etos"] — phonetically matched to English/Spanish phonology.
 *
 * Requires sync_engine.py to have populated:
 *   assets/kws_model/ — ONNX model files
 *   jniLibs/<ABI>/  — Sherpa-ONNX native .so files
 */
class VoiceEngine(private val context: Context) {
    private val TAG = "EthosVoice"

    // Audio capture constants (Sherpa-ONNX requires 16kHz mono PCM)
    private val SAMPLE_RATE = 16000
    private val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
    private val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT

    private var audioRecord: AudioRecord? = null
    private var keywordSpotter: KeywordSpotter? = null
    private var isListening = false
    private var recordingJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO)

    /** Callback invoked on the IO thread when a keyword is detected. */
    var onKeywordDetected: ((keyword: String) -> Unit)? = null

    /**
     * Initialize Sherpa-ONNX KeywordSpotter with models from assets.
     * Must be called before startListening().
     */
    fun initialize(): Boolean {
        val modelDir = resolveModelDir() ?: run {
            Log.e(TAG, "KWS model not found in assets. Run sync_engine.py --only-sherpa first.")
            return false
        }
        return try {
            val config = KeywordSpotterConfig(
                featConfig = FeatureConfig(sampleRate = SAMPLE_RATE, featureDim = 80),
                modelConfig = OnlineModelConfig(
                    transducer = OnlineTransducerModelConfig(
                        encoder = "$modelDir/encoder-epoch-12-avg-2-chunk-16-left-64.onnx",
                        decoder = "$modelDir/decoder-epoch-12-avg-2-chunk-16-left-64.onnx",
                        joiner = "$modelDir/joiner-epoch-12-avg-2-chunk-16-left-64.onnx",
                    ),
                    tokens = "$modelDir/tokens.txt",
                    numThreads = 2,
                    provider = "cpu",
                ),
                maxActivePaths = 4,
                keywordsFile = "$modelDir/keywords.txt",
                // Inline keywords as phoneme sequences (Spanish-compatible)
                keywordsScore = 1.5f,
                keywordsThreshold = 0.25f,
            )
            keywordSpotter = KeywordSpotter(config = config)
            Log.i(TAG, "Sherpa-ONNX KeywordSpotter initialized. Listening for: [ethos, etos]")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize Sherpa-ONNX: ${e.message}", e)
            false
        }
    }

    /**
     * Copy model from assets to internal storage (required by Sherpa-ONNX file path API).
     * Returns the absolute path of the model directory, or null if not found.
     */
    private fun resolveModelDir(): String? {
        val assetModelDir = "kws_model"
        val internalDir = File(context.filesDir, assetModelDir)
        if (internalDir.exists() && internalDir.list()?.isNotEmpty() == true) {
            Log.d(TAG, "Model already extracted to: ${internalDir.absolutePath}")
            return internalDir.absolutePath
        }
        return try {
            internalDir.mkdirs()
            val assets = context.assets.list(assetModelDir)
            if (assets.isNullOrEmpty()) {
                Log.e(TAG, "No assets found under: $assetModelDir")
                return null
            }
            for (asset in assets) {
                context.assets.open("$assetModelDir/$asset").use { input ->
                    File(internalDir, asset).outputStream().use { output ->
                        input.copyTo(output)
                    }
                }
            }
            Log.i(TAG, "Model extracted to: ${internalDir.absolutePath}")
            internalDir.absolutePath
        } catch (e: Exception) {
            Log.e(TAG, "Failed to extract model assets: ${e.message}")
            null
        }
    }

    /**
     * Start continuous microphone capture and keyword detection.
     * Requires RECORD_AUDIO permission to be granted.
     */
    @SuppressLint("MissingPermission")
    fun startListening() {
        if (isListening) return
        if (keywordSpotter == null) {
            Log.w(TAG, "KeywordSpotter not initialized. Call initialize() first.")
            return
        }

        val bufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)
            .takeIf { it > 0 } ?: run {
            Log.e(TAG, "Invalid audio buffer size.")
            return
        }

        try {
            audioRecord = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize,
            )

            if (audioRecord?.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord initialization failed.")
                return
            }

            val stream = keywordSpotter!!.createStream()
            audioRecord?.startRecording()
            isListening = true
            Log.i(TAG, "VoiceEngine: Continuous listening started [Sherpa-ONNX KWS].")

            recordingJob = scope.launch {
                val buffer = ShortArray(bufferSize)
                while (isListening) {
                    val read = audioRecord?.read(buffer, 0, buffer.size) ?: 0
                    if (read > 0) {
                        // Feed audio samples to Sherpa-ONNX (requires Float32 normalized)
                        val floatSamples = FloatArray(read) { buffer[it] / 32768.0f }
                        stream.acceptWaveform(floatSamples, sampleRate = SAMPLE_RATE)

                        while (keywordSpotter!!.isReady(stream)) {
                            keywordSpotter!!.decode(stream)
                        }

                        val result = keywordSpotter!!.getResult(stream)
                        if (result.keyword.isNotBlank()) {
                            Log.i(TAG, "WAKE WORD DETECTED: '${result.keyword}'")
                            onKeywordDetected?.invoke(result.keyword.trim())
                            // Reset stream for next detection cycle
                            stream.reset()
                        }
                    }
                }
                stream.release()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start VoiceEngine", e)
        }
    }

    /** Stop microphone capture and release resources. */
    fun stopListening() {
        isListening = false
        recordingJob?.cancel()
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        Log.i(TAG, "VoiceEngine: Listening stopped.")
    }

    /** Release Sherpa-ONNX resources. Call from Service.onDestroy(). */
    fun release() {
        stopListening()
        keywordSpotter?.release()
        keywordSpotter = null
    }
}
