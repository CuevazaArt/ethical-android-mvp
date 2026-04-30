// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
package com.ethos.nomad.audio

import android.content.Context
import android.util.Log
import com.k2fsa.sherpa.onnx.FeatureConfig
import com.k2fsa.sherpa.onnx.OfflineModelConfig
import com.k2fsa.sherpa.onnx.OfflineRecognizer
import com.k2fsa.sherpa.onnx.OfflineRecognizerConfig
import com.k2fsa.sherpa.onnx.OfflineWhisperModelConfig
import java.io.File
import java.util.Locale

/**
 * Sherpa-ONNX offline speech-to-text using exported Whisper tiny (multilingual).
 *
 * Models are synced into `assets/stt_model/` by `scripts/nomad/sync_engine.py --only-sherpa`.
 * Filenames inside the tarball may vary; we discover encoder/decoder/tokens under the tree.
 */
class SherpaSttEngine(private val context: Context) {

    private val TAG = "EthosSherpaStt"
    private val assetDir = "stt_model"
    private val sampleRate = 16000

    private var recognizer: OfflineRecognizer? = null

    fun isReady(): Boolean = recognizer != null

    fun initialize(): Boolean {
        if (recognizer != null) return true
        val root = resolveModelRoot() ?: run {
            Log.w(
                TAG,
                "STT assets missing under $assetDir. Run: python scripts/nomad/sync_engine.py --only-sherpa",
            )
            return false
        }
        val paths = resolveArtifacts(root) ?: run {
            Log.e(TAG, "Could not resolve encoder/decoder/tokens under ${root.absolutePath}")
            return false
        }
        val (encoderPath, decoderPath, tokensPath) = paths
        val whisperLang = Locale.getDefault().language.ifBlank { "en" }
        return try {
            val cfg = OfflineRecognizerConfig(
                featConfig = FeatureConfig(sampleRate = sampleRate, featureDim = 80),
                modelConfig = OfflineModelConfig(
                    whisper = OfflineWhisperModelConfig(
                        encoder = encoderPath,
                        decoder = decoderPath,
                        language = whisperLang,
                        task = "transcribe",
                    ),
                    tokens = tokensPath,
                    modelType = "whisper",
                    numThreads = 2,
                    debug = false,
                    provider = "cpu",
                ),
            )
            recognizer = OfflineRecognizer(config = cfg)
            Log.i(TAG, "Sherpa Whisper STT ready (lang=$whisperLang).")
            true
        } catch (e: Exception) {
            Log.e(TAG, "OfflineRecognizer init failed: ${e.message}", e)
            recognizer = null
            false
        }
    }

    fun transcribe(samples: FloatArray, sampleRateHz: Int): String? {
        val rec = recognizer ?: return null
        if (samples.isEmpty()) return null
        val stream = rec.createStream()
        return try {
            stream.acceptWaveform(samples, sampleRateHz)
            rec.decode(stream)
            rec.getResult(stream).text?.trim()?.takeIf { it.isNotEmpty() }
        } catch (e: Exception) {
            Log.e(TAG, "Sherpa decode failed: ${e.message}", e)
            null
        } finally {
            stream.release()
        }
    }

    fun release() {
        recognizer?.release()
        recognizer = null
        Log.i(TAG, "Sherpa STT released.")
    }

    private fun resolveModelRoot(): File? {
        val internalDir = File(context.filesDir, assetDir)
        if (!internalDir.exists() || !internalDir.walkTopDown().any { it.isFile }) {
            try {
                copyAssetsRecursive(assetDir, internalDir)
            } catch (e: Exception) {
                Log.e(TAG, "Failed to extract STT assets: ${e.message}", e)
                return null
            }
        }
        val tokensFile = internalDir.walkTopDown().find { it.isFile && it.name.endsWith("tokens.txt") }
        return tokensFile?.parentFile ?: internalDir
    }

    /**
     * Prefer int8 ONNX when both exist (smaller / faster on CPU).
     */
    private fun resolveArtifacts(root: File): Triple<String, String, String>? {
        val tokens = root.walkTopDown().find { it.isFile && it.name.endsWith("tokens.txt") }
            ?: return null
        val encoders = root.walkTopDown().filter {
            it.isFile && it.name.endsWith(".onnx", ignoreCase = true) &&
                it.name.contains("encoder", ignoreCase = true)
        }.sortedWith(compareBy({ !it.name.contains("int8") }, { it.name.length }))
        val decoders = root.walkTopDown().filter {
            it.isFile && it.name.endsWith(".onnx", ignoreCase = true) &&
                it.name.contains("decoder", ignoreCase = true)
        }.sortedWith(compareBy({ !it.name.contains("int8") }, { it.name.length }))
        val enc = encoders.firstOrNull() ?: return null
        val dec = decoders.firstOrNull() ?: return null
        Log.d(TAG, "STT artifacts: enc=${enc.name} dec=${dec.name} tok=${tokens.name}")
        return Triple(enc.absolutePath, dec.absolutePath, tokens.absolutePath)
    }

    private fun copyAssetsRecursive(assetPath: String, destDir: File) {
        destDir.mkdirs()
        val children = context.assets.list(assetPath) ?: emptyArray()
        if (children.isEmpty()) {
            context.assets.open(assetPath).use { input ->
                destDir.outputStream().use { output -> input.copyTo(output) }
            }
        } else {
            for (child in children) {
                copyAssetsRecursive("$assetPath/$child", File(destDir, child))
            }
        }
    }
}
