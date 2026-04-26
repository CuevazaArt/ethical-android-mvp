package com.ethos.nomad

import android.app.Service
import android.content.Intent
import android.os.Bundle
import android.os.IBinder
import android.speech.RecognitionListener
import android.speech.RecognizerIntent
import android.speech.SpeechRecognizer
import android.util.Log
import okhttp3.*
import org.json.JSONObject
import android.util.Base64
import android.media.MediaPlayer
import java.io.File
import java.io.FileOutputStream
import java.util.Locale

class NomadService : Service(), RecognitionListener {

    private val TAG = "NomadService"
    private var speechRecognizer: SpeechRecognizer? = null
    private var webSocket: WebSocket? = null
    private var mediaPlayer: MediaPlayer? = null

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Nomad Foreground Service Created")
        initWebSocket()
        initSpeechRecognizer()
    }

    private fun initWebSocket() {
        val client = OkHttpClient()
        val request = Request.Builder().url("ws://10.0.2.2:8000/ws/nomad").build() // Use 10.0.2.2 for Android Emulator to host localhost
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
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
            }
        })
    }

    private fun playBase64Audio(b64: String) {
        try {
            val audioData = Base64.decode(b64, Base64.DEFAULT)
            // Save to temp file since MediaPlayer requires a FileDescriptor or URI
            val tempFile = File.createTempFile("ethos_tts", ".mp3", cacheDir)
            tempFile.deleteOnExit()
            FileOutputStream(tempFile).use { it.write(audioData) }

            mediaPlayer?.release()
            mediaPlayer = MediaPlayer().apply {
                setDataSource(tempFile.absolutePath)
                setOnCompletionListener {
                    it.release()
                    mediaPlayer = null
                    // Resume listening after Ethos finishes speaking (Acoustic Echo Shield natively)
                    startListening()
                }
                prepare()
                start()
            }
            
            // Stop listening while speaking to avoid self-feedback loop
            speechRecognizer?.stopListening()
            
        } catch (e: Exception) {
            Log.e(TAG, "Error playing audio", e)
            startListening() // fallback
        }
    }

    private fun initSpeechRecognizer() {
        if (SpeechRecognizer.isRecognitionAvailable(this)) {
            speechRecognizer = SpeechRecognizer.createSpeechRecognizer(this)
            speechRecognizer?.setRecognitionListener(this)
            startListening()
        } else {
            Log.e(TAG, "Speech Recognition not available")
        }
    }

    private fun startListening() {
        val intent = Intent(RecognizerIntent.ACTION_RECOGNIZE_SPEECH).apply {
            putExtra(RecognizerIntent.EXTRA_LANGUAGE_MODEL, RecognizerIntent.LANGUAGE_MODEL_FREE_FORM)
            putExtra(RecognizerIntent.EXTRA_LANGUAGE, Locale.getDefault())
            putExtra(RecognizerIntent.EXTRA_PARTIAL_RESULTS, true)
        }
        speechRecognizer?.startListening(intent)
    }

    // RecognitionListener Callbacks
    override fun onResults(results: Bundle?) {
        val matches = results?.getStringArrayList(SpeechRecognizer.RESULTS_RECOGNITION)
        if (!matches.isNullOrEmpty()) {
            val text = matches[0]
            Log.d(TAG, "Heard: $text")
            
            // Send to Ethos Kernel
            val payload = JSONObject()
            payload.put("type", "user_speech")
            payload.put("text", text)
            webSocket?.send(payload.toString())
        }
        // Restart listening loop
        startListening()
    }

    override fun onError(error: Int) {
        Log.e(TAG, "Speech Error: $error")
        // Restart on error (e.g., timeout)
        startListening()
    }

    override fun onReadyForSpeech(params: Bundle?) {}
    override fun onBeginningOfSpeech() {}
    override fun onRmsChanged(rmsdB: Float) {}
    override fun onBufferReceived(buffer: ByteArray?) {}
    override fun onEndOfSpeech() {}
    override fun onPartialResults(partialResults: Bundle?) {}
    override fun onEvent(eventType: Int, params: Bundle?) {}

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Nomad Foreground Service Started")
        // TODO: Start Foreground Notification here
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? = null

    override fun onDestroy() {
        super.onDestroy()
        speechRecognizer?.destroy()
        mediaPlayer?.release()
        webSocket?.close(1000, "Service destroyed")
        Log.d(TAG, "Nomad Foreground Service Destroyed")
    }
}
