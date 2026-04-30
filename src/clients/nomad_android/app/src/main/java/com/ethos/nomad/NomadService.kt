// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log
import okhttp3.*
import org.json.JSONObject
import android.util.Base64
import android.media.MediaPlayer
import java.io.File
import java.io.FileOutputStream
import android.app.Notification
import android.app.NotificationChannel
import android.app.NotificationManager
import android.os.Build
import android.os.Handler
import android.os.Looper
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import androidx.core.app.NotificationCompat
import com.ethos.nomad.audio.VoiceEngine
import java.util.Locale

/**
 * NomadService — Foreground service for persistent cognition pipeline.
 *
 * V2.95 responsibilities:
 *   - Sherpa-ONNX Wake Word detection (VoiceEngine, background AudioRecord)
 *   - WebSocket bridge to /ws/nomad (TTS audio, autonomous pulses)
 *   - MediaPlayer for server-side TTS audio playback (Base64 → MP3)
 *   - Foreground notification for Android process persistence
 */
class NomadService : Service() {

    private val TAG = "NomadService"
    private val okHttpClient = OkHttpClient()
    private var webSocket: WebSocket? = null
    private var mediaPlayer: MediaPlayer? = null
    private val voiceEngine by lazy { VoiceEngine(this) }
    private var speechRecognizer: SpeechRecognizer? = null
    @Volatile private var sttInProgress = false
    private var lastWakeWordAtMs = 0L

    private val NOTIFICATION_ID = 1
    private val CHANNEL_ID = "NomadServiceChannel"
    private val handler = Handler(Looper.getMainLooper())
    private val RECONNECT_DELAY_MS = 5000L
    private val STT_TIMEOUT_MS = 8000L
    private val WAKE_WORD_COOLDOWN_MS = 1500L
    private var sttTimeoutRunnable: Runnable? = null

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Nomad Foreground Service Created (Sherpa-ONNX KWS enabled)")
        createNotificationChannel()
        initWebSocket()
        initSpeechRecognizer()
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
                    Log.d(TAG, "STT ready for speech.")
                }

                override fun onBeginningOfSpeech() {
                    Log.d(TAG, "STT speech started.")
                }

                override fun onRmsChanged(rmsdB: Float) = Unit
                override fun onBufferReceived(buffer: ByteArray?) = Unit
                override fun onEndOfSpeech() {
                    Log.d(TAG, "STT speech ended.")
                }

                override fun onError(error: Int) {
                    Log.w(TAG, "STT error: ${sttErrorName(error)} ($error)")
                    completeSttAndResumeListening()
                }

                override fun onResults(results: android.os.Bundle?) {
                    val text = results
                        ?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
                        ?.firstOrNull()
                        ?.trim()
                        .orEmpty()
                    if (text.isNotEmpty()) {
                        Log.i(TAG, "STT transcript: \"$text\"")
                        sendUserSpeech(text)
                    } else {
                        Log.d(TAG, "STT produced empty transcript.")
                    }
                    completeSttAndResumeListening()
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

        // Pause KWS while STT uses the microphone.
        voiceEngine.stopListening()

        // Keep backward-compatible pulse for observability.
        val pulse = JSONObject().apply {
            put("type", "wake_word")
            put("keyword", keyword)
        }
        webSocket?.send(pulse.toString())

        val recognizer = speechRecognizer
        if (recognizer == null) {
            Log.w(TAG, "SpeechRecognizer unavailable; resuming wake-word listening.")
            voiceEngine.startListening()
            return
        }

        sttInProgress = true
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, false)
            putExtra(RecognizerIntent.EXTRA_MAX_RESULTS, 1)
            putExtra(RecognizerIntent.EXTRA_CALLING_PACKAGE, packageName)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault().toLanguageTag())
        }
        recognizer.startListening(intent)

        // Safety timeout so KWS always resumes even if callback is lost.
        sttTimeoutRunnable = Runnable {
            if (sttInProgress) {
                Log.w(TAG, "STT timeout reached; forcing recovery.")
                completeSttAndResumeListening()
            }
        }
        handler.postDelayed(sttTimeoutRunnable!!, STT_TIMEOUT_MS)
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

    private fun completeSttAndResumeListening() {
        if (!sttInProgress) return
        sttInProgress = false
        sttTimeoutRunnable?.let(handler::removeCallbacks)
        sttTimeoutRunnable = null
        // Small delay avoids immediate mic contention on some devices.
        handler.postDelayed(
            { voiceEngine.startListening() },
            250L
        )
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
                NotificationManager.IMPORTANCE_LOW
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
        // Must run on main thread for MediaPlayer
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
        
        // V2.95: Start Sherpa-ONNX continuous background listening
        voiceEngine.startListening()

        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer?.cancel()
        speechRecognizer?.destroy()
        speechRecognizer = null
        voiceEngine.release()
        mediaPlayer?.release()
        webSocket?.close(1000, "Service destroyed")
        okHttpClient.dispatcher.executorService.shutdown()
        Log.d(TAG, "Nomad Foreground Service Destroyed")
    }
}
