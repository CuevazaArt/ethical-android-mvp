// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.audio

import android.annotation.SuppressLint
import android.content.Context
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaRecorder
import android.util.Log
import com.k2fsa.sherpa.onnx.FeatureConfig
import com.k2fsa.sherpa.onnx.KeywordSpotter
import com.k2fsa.sherpa.onnx.KeywordSpotterConfig
import com.k2fsa.sherpa.onnx.OnlineModelConfig
import com.k2fsa.sherpa.onnx.OnlineTransducerModelConfig
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
 * Requires sync_engine.py --only-sherpa to have populated:
 *   assets/kws_model/ — ONNX model files
 *   jniLibs/<ABI>/    — Sherpa-ONNX native .so files
 *
 * Security:
 *   - isListening is @Volatile to prevent race conditions between the recording
 *     coroutine and stopListening() called from the main/service thread.
 *   - Model extraction only writes to app-private internal storage (filesDir).
 *   - AudioRecord is released on stopListening() to prevent mic lock.
 */
class VoiceEngine(private val context: Context) {
    private val TAG = "EthosVoice"

    // Sherpa-ONNX requires 16kHz mono PCM
    private val SAMPLE_RATE = 16000
    private val CHANNEL_CONFIG = AudioFormat.CHANNEL_IN_MONO
    private val AUDIO_FORMAT = AudioFormat.ENCODING_PCM_16BIT

    private var audioRecord: AudioRecord? = null
    private var keywordSpotter: KeywordSpotter? = null

    // @Volatile: ensures visibility across threads — no race on stopListening()
    @Volatile private var isListening = false
    private var recordingJob: Job? = null
    private val scope = CoroutineScope(Dispatchers.IO)

    /** Callback invoked on the IO thread when a keyword is detected. */
    var onKeywordDetected: ((keyword: String) -> Unit)? = null

    /**
     * Initialize Sherpa-ONNX KeywordSpotter with models from assets.
     * Must be called before startListening(). Safe to call multiple times.
     */
    fun initialize(): Boolean {
        if (keywordSpotter != null) {
            Log.d(TAG, "Already initialized.")
            return true
        }
        val modelDir = resolveModelDir() ?: run {
            Log.e(TAG, "KWS model not found in assets. Run: python scripts/nomad/sync_engine.py --only-sherpa")
            return false
        }
        return try {
            // Hard filenames match the wenetspeech 3.3M model release
            val config = KeywordSpotterConfig(
                featConfig = FeatureConfig(sampleRate = SAMPLE_RATE, featureDim = 80),
                modelConfig = OnlineModelConfig(
                    transducer = OnlineTransducerModelConfig(
                        encoder = "$modelDir/encoder-epoch-12-avg-2-chunk-16-left-64.onnx",
                        decoder = "$modelDir/decoder-epoch-12-avg-2-chunk-16-left-64.onnx",
                        joiner  = "$modelDir/joiner-epoch-12-avg-2-chunk-16-left-64.onnx",
                    ),
                    tokens = "$modelDir/tokens.txt",
                    numThreads = 2,
                    provider = "cpu",
                ),
                maxActivePaths = 4,
                keywordsFile = "$modelDir/keywords.txt",
                keywordsScore = 1.5f,
                keywordsThreshold = 0.25f,
            )
            keywordSpotter = KeywordSpotter(config = config)
            Log.i(TAG, "Sherpa-ONNX KeywordSpotter ready. Listening for: [ethos, etos]")
            true
        } catch (e: Exception) {
            Log.e(TAG, "Failed to initialize Sherpa-ONNX: ${e.message}", e)
            false
        }
    }

    /**
     * Recursively copy model from assets to app-private internal storage.
     * Required because Sherpa-ONNX uses file-path API, not assets stream.
     * Returns absolute path of the model dir, or null if not found.
     */
    private fun resolveModelDir(): String? {
        val assetModelDir = "kws_model"
        val internalDir = File(context.filesDir, assetModelDir)

        // If already extracted and non-empty, reuse
        if (internalDir.exists() && internalDir.walkTopDown().any { it.isFile }) {
            Log.d(TAG, "Model cache hit: ${internalDir.absolutePath}")
            return internalDir.absolutePath
        }

        return try {
            copyAssetsRecursive(assetModelDir, internalDir)
            Log.i(TAG, "Model extracted to: ${internalDir.absolutePath}")
            internalDir.absolutePath
        } catch (e: Exception) {
            Log.e(TAG, "Failed to extract model assets: ${e.message}", e)
            null
        }
    }

    /**
     * Recursively copy an asset directory to the filesystem.
     * Handles models packaged with sub-directories (e.g. test_wavs/).
     */
    private fun copyAssetsRecursive(assetPath: String, destDir: File) {
        destDir.mkdirs()
        val children = context.assets.list(assetPath) ?: emptyArray()
        if (children.isEmpty()) {
            // It's a file — copy it
            context.assets.open(assetPath).use { input ->
                destDir.outputStream().use { output -> input.copyTo(output) }
            }
        } else {
            for (child in children) {
                copyAssetsRecursive("$assetPath/$child", File(destDir, child))
            }
        }
    }

    /**
     * Start continuous microphone capture and keyword detection.
     * Requires RECORD_AUDIO permission to be granted by the caller.
     */
    @SuppressLint("MissingPermission")
    fun startListening() {
        if (isListening) return
        val kws = keywordSpotter ?: run {
            Log.w(TAG, "Not initialized. Call initialize() first.")
            return
        }

        val bufferSize = AudioRecord.getMinBufferSize(SAMPLE_RATE, CHANNEL_CONFIG, AUDIO_FORMAT)
        if (bufferSize <= 0) {
            Log.e(TAG, "Invalid audio buffer size: $bufferSize")
            return
        }

        try {
            val ar = AudioRecord(
                MediaRecorder.AudioSource.MIC,
                SAMPLE_RATE,
                CHANNEL_CONFIG,
                AUDIO_FORMAT,
                bufferSize,
            )
            if (ar.state != AudioRecord.STATE_INITIALIZED) {
                Log.e(TAG, "AudioRecord failed to initialize.")
                ar.release()
                return
            }

            audioRecord = ar
            val stream = kws.createStream()
            ar.startRecording()
            isListening = true
            Log.i(TAG, "VoiceEngine: Listening started [Sherpa-ONNX KWS active].")

            recordingJob = scope.launch {
                val buffer = ShortArray(bufferSize)
                while (isListening) {
                    val read = ar.read(buffer, 0, buffer.size)
                    if (read > 0) {
                        val floatSamples = FloatArray(read) { buffer[it] / 32768.0f }
                        stream.acceptWaveform(floatSamples, sampleRate = SAMPLE_RATE)

                        while (kws.isReady(stream)) {
                            kws.decode(stream)
                        }

                        val result = kws.getResult(stream)
                        if (result.keyword.isNotBlank()) {
                            Log.i(TAG, "WAKE WORD: '${result.keyword}'")
                            onKeywordDetected?.invoke(result.keyword.trim())
                            stream.reset()
                        }
                    }
                }
                stream.release()
            }
        } catch (e: Exception) {
            Log.e(TAG, "Failed to start VoiceEngine", e)
            isListening = false
        }
    }

    /** Stop microphone capture and release the hardware resource. */
    fun stopListening() {
        isListening = false
        recordingJob?.cancel()
        recordingJob = null
        audioRecord?.stop()
        audioRecord?.release()
        audioRecord = null
        Log.i(TAG, "VoiceEngine: Listening stopped.")
    }

    /**
     * Release all resources. Call from Service.onDestroy().
     * Safe to call even if never started.
     */
    fun release() {
        stopListening()
        keywordSpotter?.release()
        keywordSpotter = null
        Log.i(TAG, "VoiceEngine: Released.")
    }
}
