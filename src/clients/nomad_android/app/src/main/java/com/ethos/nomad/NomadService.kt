// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad

import android.annotation.SuppressLint
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.app.Service
import android.content.Intent
import android.media.AudioFormat
import android.media.AudioRecord
import android.media.MediaPlayer
import android.media.MediaRecorder
import android.os.Build
import android.os.Handler
import android.os.IBinder
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Base64
import android.util.Log
import androidx.core.app.NotificationCompat
import com.ethos.nomad.audio.SherpaSttEngine
import com.ethos.nomad.audio.VoiceEngine
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.isActive
import kotlinx.coroutines.launch
import kotlinx.coroutines.withContext
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import org.json.JSONObject
import java.io.File
import java.io.FileOutputStream
import java.util.Locale
import kotlin.math.sqrt

/**
 * NomadService — Foreground service for persistent cognition pipeline.
 *
 * Voice stack:
 * - Sherpa-ONNX wake word (VoiceEngine)
 * - Sherpa-ONNX Whisper offline STT when `assets/stt_model` is synced (see sync_engine.py)
 * - Android SpeechRecognizer fallback when Sherpa STT is unavailable or yields no text
 * - WebSocket `/ws/nomad` for turns + server TTS playback
 */
class NomadService : Service() {

    private val TAG = "NomadService"
    private val okHttpClient = OkHttpClient()
    private var webSocket: WebSocket? = null
    private var mediaPlayer: MediaPlayer? = null
    private val voiceEngine by lazy { VoiceEngine(this) }
    private val sherpaStt by lazy { SherpaSttEngine(this) }
    private val sttSupervisor = SupervisorJob()
    private val sttScope = CoroutineScope(sttSupervisor + Dispatchers.IO)

    private var speechRecognizer: SpeechRecognizer? = null
    @Volatile private var sttInProgress = false
    private var lastWakeWordAtMs = 0L
    private var sttJob: Job? = null

    private val NOTIFICATION_ID = 1
    private val CHANNEL_ID = "NomadServiceChannel"
    private val handler = Handler(Looper.getMainLooper())
    private val RECONNECT_DELAY_MS = 5000L
    /** Covers PCM capture + Whisper decode + optional native STT. */
    private val STT_SESSION_TIMEOUT_MS = 20000L
    private val WAKE_WORD_COOLDOWN_MS = 1500L
    private var sttTimeoutRunnable: Runnable? = null

    private val captureSampleRate = 16000
    private val maxUtteranceMs = 8000
    private val minUtteranceMs = 300
    private val silenceRmsThreshold = 0.012f
    private val silenceHoldMs = 700L

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Nomad Foreground Service Created (Sherpa-ONNX KWS enabled)")
        createNotificationChannel()
        initWebSocket()
        initSpeechRecognizer()
        val sttOk = sherpaStt.initialize()
        Log.d(TAG, "Sherpa offline STT init: ${if (sttOk) "OK" else "skipped/fallback"}")
        initVoiceEngine()
    }

    private fun initVoiceEngine() {
        val ready = voiceEngine.initialize()
        if (ready) {
            voiceEngine.onKeywordDetected = { keyword ->
                onWakeWordDetected(keyword)
            }
        } else {
            Log.w(TAG, "VoiceEngine failed to initialize — Wake Word disabled.")
        }
    }

    private fun initSpeechRecognizer() {
        if (!SpeechRecognizer.isRecognitionAvailable(this)) {
            Log.w(TAG, "SpeechRecognizer is not available on this device.")
            return
        }
        speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this).apply {
            setRecognitionListener(object : RecognitionListener {
                override fun onReadyForSpeech(params: android.os.Bundle?) {
                    Log.d(TAG, "Native STT ready for speech.")
                }

                override fun onBeginningOfSpeech() {
                    Log.d(TAG, "Native STT speech started.")
                }

                override fun onRmsChanged(rmsdB: Float) = Unit
                override fun onBufferReceived(buffer: ByteArray?) = Unit
                override fun onEndOfSpeech() {
                    Log.d(TAG, "Native STT speech ended.")
                }

                override fun onError(error: Int) {
                    Log.w(TAG, "Native STT error: ${sttErrorName(error)} ($error)")
                    finishSttSession()
                }

                override fun onResults(results: android.os.Bundle?) {
                    val text = results
                        ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        ?.firstOrNull()
                        ?.trim()
                        .orEmpty()
                    if (text.isNotEmpty()) {
                        Log.i(TAG, "Native STT transcript: \"$text\"")
                        sendUserSpeech(text)
                    } else {
                        Log.d(TAG, "Native STT produced empty transcript.")
                    }
                    finishSttSession()
                }

                override fun onPartialResults(partialResults: android.os.Bundle?) = Unit
                override fun onEvent(eventType: Int, params: android.os.Bundle?) = Unit
            })
        }
    }

    private fun onWakeWordDetected(keyword: String) {
        val now = System.currentTimeMillis()
        if (sttInProgress) {
            Log.d(TAG, "Wake word ignored while STT is running.")
            return
        }
        if ((now - lastWakeWordAtMs) < WAKE_WORD_COOLDOWN_MS) {
            Log.d(TAG, "Wake word ignored due to cooldown.")
            return
        }
        lastWakeWordAtMs = now
        Log.i(TAG, "Wake word received: '$keyword' — starting STT turn.")

        voiceEngine.stopListening()

        val pulse = JSONObject().apply {
            put("type", "wake_word")
            put("keyword", keyword)
        }
        webSocket?.send(pulse.toString())

        sttInProgress = true
        sttTimeoutRunnable = Runnable {
            Log.w(TAG, "STT session timeout; forcing recovery.")
            try {
                speechRecognizer?.cancel()
            } catch (_: Exception) {
                // ignore
            }
            finishSttSession()
        }
        handler.postDelayed(sttTimeoutRunnable!!, STT_SESSION_TIMEOUT_MS)

        sttJob = sttScope.launch {
            try {
                val pcm = captureUtterancePcm()
                val sherpaText = if (pcm != null && sherpaStt.isReady()) {
                    sherpaStt.transcribe(pcm, captureSampleRate)?.trim().orEmpty()
                } else {
                    ""
                }
                if (sherpaText.isNotEmpty()) {
                    handler.post {
                        Log.i(TAG, "Sherpa STT transcript: \"$sherpaText\"")
                        sendUserSpeech(sherpaText)
                        finishSttSession()
                    }
                } else {
                    handler.post {
                        startAndroidSpeechFallback()
                    }
                }
            } catch (e: Exception) {
                Log.e(TAG, "Sherpa STT pipeline error", e)
                handler.post {
                    startAndroidSpeechFallback()
                }
            }
        }
    }

    private fun startAndroidSpeechFallback() {
        if (!sttInProgress) return
        val recognizer = speechRecognizer
        if (recognizer == null) {
            Log.w(TAG, "SpeechRecognizer unavailable; resuming wake-word listening.")
            finishSttSession()
            return
        }
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, packageName)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag())
        }
        try {
            recognizer.startListening(intent)
        } catch (e: Exception) {
            Log.e(TAG, "SpeechRecognizer.startListening failed", e)
            finishSttSession()
        }
    }

    @SuppressLint("MissingPermission")
    private suspend fun captureUtterancePcm(): FloatArray? = withContext(Dispatchers.IO) {
        val channelConfig = AudioFormat.CHANNEL_IN_MONO
        val audioFormat = AudioFormat.ENCODING_PCM_16BIT
        val bufSize = AudioRecord.getMinBufferSize(captureSampleRate, channelConfig, audioFormat)
        if (bufSize <= 0) return@withContext null

        val ar = try {
            AudioRecord(
                MediaRecorder.AudioSource.VOICE_RECOGNITION,
                captureSampleRate,
                channelConfig,
                audioFormat,
                bufSize * 2,
            )
        } catch (e: Exception) {
            Log.e(TAG, "AudioRecord allocation failed", e)
            return@withContext null
        }

        if (ar.state != AudioRecord.STATE_INITIALIZED) {
            ar.release()
            return@withContext null
        }

        val maxSamples = captureSampleRate * (maxUtteranceMs / 1000)
        val minSamples = captureSampleRate * minUtteranceMs / 1000
        val scratch = ShortArray(bufSize)
        val accumulation = ShortArray(maxSamples)
        var written = 0
        var trailingSilenceStart: Long = -1L
        val deadlineMs = System.currentTimeMillis() + maxUtteranceMs

        ar.startRecording()
        try {
            while (written < maxSamples && System.currentTimeMillis() < deadlineMs && isActive) {
                val toRead = minOf(scratch.size, maxSamples - written)
                val n = ar.read(scratch, 0, toRead)
                if (n <= 0) continue

                var sumSq = 0.0
                for (i in 0 until n) {
                    val s = scratch[i].toFloat() / 32768f
                    sumSq += (s * s).toDouble()
                }
                val rms = sqrt(sumSq / n).toFloat()

                System.arraycopy(scratch, 0, accumulation, written, n)
                written += n

                if (written >= minSamples && rms < silenceRmsThreshold) {
                    if (trailingSilenceStart < 0L) {
                        trailingSilenceStart = System.currentTimeMillis()
                    } else if (System.currentTimeMillis() - trailingSilenceStart > silenceHoldMs) {
                        break
                    }
                } else {
                    trailingSilenceStart = -1L
                }
            }
        } finally {
            try {
                ar.stop()
            } catch (_: Exception) {
                // ignore
            }
            ar.release()
        }

        if (written < minSamples) return@withContext null
        FloatArray(written) { accumulation[it] / 32768f }
    }

    private fun sendUserSpeech(text: String) {
        val payload = JSONObject().apply {
            put("type", "user_speech")
            put("text", text)
        }
        val sent = webSocket?.send(payload.toString()) ?: false
        if (!sent) {
            Log.w(TAG, "Failed to send user_speech frame — WebSocket not ready.")
        }
    }

    private fun finishSttSession() {
        sttTimeoutRunnable?.let(handler::removeCallbacks)
        sttTimeoutRunnable = null
        sttJob?.cancel()
        sttJob = null
        try {
            speechRecognizer?.stopListening()
        } catch (_: Exception) {
            // ignore
        }
        val wasActive = sttInProgress
        sttInProgress = false
        if (wasActive) {
            handler.postDelayed(
                { voiceEngine.startListening() },
                250L,
            )
        }
    }

    private fun sttErrorName(code: Int): String = when (code) {
        SpeechRecognizer.ERROR_AUDIO -> "ERROR_AUDIO"
        SpeechRecognizer.ERROR_CLIENT -> "ERROR_CLIENT"
        SpeechRecognizer.ERROR_INSUFFICIENT_PERMISSIONS -> "ERROR_INSUFFICIENT_PERMISSIONS"
        SpeechRecognizer.ERROR_NETWORK -> "ERROR_NETWORK"
        SpeechRecognizer.ERROR_NETWORK_TIMEOUT -> "ERROR_NETWORK_TIMEOUT"
        SpeechRecognizer.ERROR_NO_MATCH -> "ERROR_NO_MATCH"
        SpeechRecognizer.ERROR_RECOGNIZER_BUSY -> "ERROR_RECOGNIZER_BUSY"
        SpeechRecognizer.ERROR_SERVER -> "ERROR_SERVER"
        SpeechRecognizer.ERROR_SPEECH_TIMEOUT -> "ERROR_SPEECH_TIMEOUT"
        else -> "ERROR_UNKNOWN"
    }

    private fun createNotificationChannel() {
        if (Build.VERSION.SDK_INT >= Build.VERSION_CODES.O) {
            val serviceChannel = NotificationChannel(
                CHANNEL_ID,
                "Ethos Nomad Service",
                NotificationManager.IMPORTANCE_LOW,
            )
            val manager = getSystemService(NotificationManager::class.java)
            manager?.createNotificationChannel(serviceChannel)
        }
    }

    private fun initWebSocket() {
        val request = Request.Builder().url("ws://10.0.2.2:8000/ws/nomad").build()
        webSocket = okHttpClient.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d(TAG, "WebSocket Opened")
            }

            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json = JSONObject(text)
                    if (json.has("type") && json.getString("type") == "tts_audio") {
                        val b64Audio = json.optString("audio_b64", "")
                        if (b64Audio.isNotEmpty()) {
                            playBase64Audio(b64Audio)
                        }
                    } else if (json.has("type") && json.getString("type") == "autonomous_pulse") {
                        Log.d(TAG, "Autonomous Pulse: ${json.optString("description")}")
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error parsing server message", e)
                }
            }

            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket Error", t)
                scheduleReconnect()
            }

            override fun onClosed(webSocket: WebSocket, code: Int, reason: String) {
                Log.d(TAG, "WebSocket Closed: $reason")
                scheduleReconnect()
            }
        })
    }

    private fun scheduleReconnect() {
        Log.d(TAG, "Scheduling WebSocket reconnect in ${RECONNECT_DELAY_MS}ms")
        handler.postDelayed({
            initWebSocket()
        }, RECONNECT_DELAY_MS)
    }

    private fun playBase64Audio(b64: String) {
        handler.post {
            try {
                val audioData = Base64.decode(b64, Base64.DEFAULT)
                val tempFile = File.createTempFile("ethos_tts", ".mp3", cacheDir)
                tempFile.deleteOnExit()
                FileOutputStream(tempFile).use { it.write(audioData) }

                mediaPlayer?.release()
                mediaPlayer = MediaPlayer().apply {
                    setDataSource(tempFile.absolutePath)
                    setOnCompletionListener {
                        it.release()
                        mediaPlayer = null
                    }
                    prepare()
                    start()
                }
            } catch (e: Exception) {
                Log.e(TAG, "Error playing audio", e)
            }
        }
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Nomad Foreground Service Started")

        val notification: Notification = NotificationCompat.Builder(this, CHANNEL_ID)
            .setContentTitle("Ethos Kernel Active")
            .setContentText("Connected to Ethos server.")
            .setSmallIcon(android.R.drawable.ic_dialog_info)
            .build()

        startForeground(NOTIFICATION_ID, notification)

        voiceEngine.startListening()

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        sttSupervisor.cancel()
        speechRecognizer?.cancel()
        speechRecognizer?.destroy()
        speechRecognizer = null
        sherpaStt.release()
        voiceEngine.release()
        mediaPlayer?.release()
        webSocket?.close(1000, "Service destroyed")
        okHttpClient.dispatcher.executorService.shutdown()
        Log.d(TAG, "Nomad Foreground Service Destroyed")
    }
}
