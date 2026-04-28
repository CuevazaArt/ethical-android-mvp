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
import androidx.core.app.NotificationCompat
import com.ethos.nomad.audio.VoiceEngine

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

    private val NOTIFICATION_ID = 1
    private val CHANNEL_ID = "NomadServiceChannel"
    private val handler = Handler(Looper.getMainLooper())
    private val RECONNECT_DELAY_MS = 5000L

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Nomad Foreground Service Created (Sherpa-ONNX KWS enabled)")
        createNotificationChannel()
        initWebSocket()
        initVoiceEngine()
    }

    private fun initVoiceEngine() {
        val ready = voiceEngine.initialize()
        if (ready) {
            voiceEngine.onKeywordDetected = { keyword ->
                Log.i(TAG, "Wake word received: '$keyword' — triggering cognitive cycle")
                // TODO Fase 25+: Trigger STT → HybridInference → TTS
                // For now, send a WebSocket pulse to the backend
                val payload = org.json.JSONObject().apply {
                    put("type", "wake_word")
                    put("keyword", keyword)
                }
                webSocket?.send(payload.toString())
            }
        } else {
            Log.w(TAG, "VoiceEngine failed to initialize — Wake Word disabled.")
        }
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
        voiceEngine.release()
        mediaPlayer?.release()
        webSocket?.close(1000, "Service destroyed")
        okHttpClient.dispatcher.executorService.shutdown()
        Log.d(TAG, "Nomad Foreground Service Destroyed")
    }
}
