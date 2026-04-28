// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.ui

import android.app.Application
import android.media.MediaPlayer
import android.util.Base64
import android.util.Log
import androidx.compose.runtime.mutableStateListOf
import androidx.compose.runtime.mutableStateOf
import androidx.lifecycle.AndroidViewModel
import androidx.lifecycle.viewModelScope
import com.ethos.nomad.persistence.MemoryBridge
import kotlinx.coroutines.launch
import okhttp3.*
import org.json.JSONObject
import java.io.File

// ── Data Models ──────────────────────────────────────────────────

data class ChatMessage(
    val text: String,
    val isUser: Boolean,
    val isBlocked: Boolean = false,
    val blockReason: String? = null,
    val ethicsContext: String? = null,
    val latencyMs: Long? = null,
    val pluginUsed: String? = null,
    val timestamp: Long = System.currentTimeMillis()
)

data class EthicsMetadata(
    val context: String = "",
    val risk: Float = 0f,
    val urgency: Float = 0f,
    val hostility: Float = 0f,
    val chosenAction: String = "",
    val verdict: String = ""
)

// ── ViewModel ────────────────────────────────────────────────────

class ChatViewModel(application: Application) : AndroidViewModel(application) {

    companion object {
        private const val TAG = "ChatViewModel"
        private const val WS_URL = "ws://10.0.2.2:8000/ws/chat"
        private const val RECONNECT_DELAY_MS = 3000L
    }

    private val memoryBridge = MemoryBridge(application)

    // ── Observable State ─────────────────────────────────────────

    /** Full message history */
    val messages = mutableStateListOf<ChatMessage>()

    /** Accumulated streaming text from current Ethos response */
    val streamingText = mutableStateOf("")

    /** True while tokens are arriving */
    val isThinking = mutableStateOf(false)

    /** True when WebSocket is connected */
    val isConnected = mutableStateOf(false)

    /** Current turn's ethics metadata */
    val currentMetadata = mutableStateOf(EthicsMetadata())

    /** Vault key pending user authorization (null = no pending request) */
    val pendingVaultKey = mutableStateOf<String?>(null)

    /** True while TTS audio is playing */
    val isSpeaking = mutableStateOf(false)

    // ── Private State ────────────────────────────────────────────

    private val client = OkHttpClient()
    private var webSocket: WebSocket? = null
    private val _streamBuffer = StringBuilder()
    private var mediaPlayer: MediaPlayer? = null
    private var tempAudioFile: File? = null

    // ── Lifecycle ────────────────────────────────────────────────

    init {
        connect()
        loadHistory()
    }

    private fun loadHistory() {
        viewModelScope.launch {
            val history = memoryBridge.loadRecent(50)
            if (history.isNotEmpty()) {
                messages.addAll(history)
                Log.d(TAG, "Loaded ${history.size} messages from local memory.")
            }
        }
    }

    private fun persistMessage(message: ChatMessage) {
        viewModelScope.launch {
            memoryBridge.save(message)
        }
    }

    private fun connect() {
        val request = Request.Builder().url(WS_URL).build()

        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                Log.i(TAG, "WebSocket connected to $WS_URL")
                isConnected.value = true
            }

            override fun onMessage(ws: WebSocket, text: String) {
                handleServerFrame(text)
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket failure: ${t.message}")
                isConnected.value = false
                scheduleReconnect()
            }

            override fun onClosed(ws: WebSocket, code: Int, reason: String) {
                Log.i(TAG, "WebSocket closed: $reason")
                isConnected.value = false
                scheduleReconnect()
            }
        })
    }

    private fun scheduleReconnect() {
        android.os.Handler(android.os.Looper.getMainLooper()).postDelayed({
            if (!isConnected.value) {
                Log.d(TAG, "Attempting reconnect...")
                connect()
            }
        }, RECONNECT_DELAY_MS)
    }

    // ── Frame Handler ────────────────────────────────────────────

    private fun handleServerFrame(raw: String) {
        try {
            val json = JSONObject(raw)
            when (json.optString("type")) {
                "metadata" -> {
                    // First event in a turn — ethics signals
                    val signals = json.optJSONObject("signals")
                    val evaluation = json.optJSONObject("evaluation")
                    currentMetadata.value = EthicsMetadata(
                        context = json.optString("context", ""),
                        risk = signals?.optDouble("risk", 0.0)?.toFloat() ?: 0f,
                        urgency = signals?.optDouble("urgency", 0.0)?.toFloat() ?: 0f,
                        hostility = signals?.optDouble("hostility", 0.0)?.toFloat() ?: 0f,
                        chosenAction = evaluation?.optString("chosen", "") ?: "",
                        verdict = evaluation?.optString("verdict", "") ?: ""
                    )
                    // Start thinking state
                    isThinking.value = true
                    _streamBuffer.clear()
                    streamingText.value = ""
                }

                "token" -> {
                    // Streaming token — accumulate
                    val content = json.optString("content", "")
                    _streamBuffer.append(content)
                    streamingText.value = _streamBuffer.toString()
                }

                "clear_tokens" -> {
                    // Plugin intercepted mid-stream — clear partial output
                    _streamBuffer.clear()
                    streamingText.value = ""
                }

                "done" -> {
                    // Turn complete
                    isThinking.value = false
                    val message = json.optString("message", "")
                    val blocked = json.optBoolean("blocked", false)
                    val reason = json.optString("reason", "")
                    val latency = json.optJSONObject("latency")
                    val totalMs = latency?.optLong("total") ?: 0L
                    val pluginUsed = json.optString("plugin_used", "")
                    val rawVaultKey = json.optString("vault_key", "")
                    val vaultKey = if (rawVaultKey == "null") "" else rawVaultKey

                    if (message.isNotEmpty()) {
                        val assistantMsg = ChatMessage(
                            text = message,
                            isUser = false,
                            isBlocked = blocked,
                            blockReason = if (blocked) reason else null,
                            ethicsContext = currentMetadata.value.context,
                            latencyMs = if (totalMs > 0) totalMs else null,
                            pluginUsed = pluginUsed.ifEmpty { null }
                        )
                        messages.add(assistantMsg)
                        persistMessage(assistantMsg)
                    }
                    streamingText.value = ""
                    _streamBuffer.clear()

                    // Vault authorization request
                    if (vaultKey.isNotEmpty()) {
                        pendingVaultKey.value = vaultKey
                    }
                }

                "tts_audio" -> {
                    // V2.82 Cycle 2: Play TTS audio from Base64 MP3
                    val b64 = json.optString("audio_b64", "")
                    if (b64.isNotEmpty()) {
                        Log.d(TAG, "TTS audio received (${b64.length} chars b64)")
                        playBase64Audio(b64)
                    }
                }
            }
        } catch (e: Exception) {
            Log.e(TAG, "Error parsing server frame", e)
        }
    }

    // ── Public API ───────────────────────────────────────────────

    fun sendMessage(text: String) {
        val trimmed = text.trim()
        if (trimmed.isEmpty()) return

        // Add user message to UI immediately
        val userMsg = ChatMessage(text = trimmed, isUser = true)
        messages.add(userMsg)
        persistMessage(userMsg)

        // Send to server
        val payload = JSONObject().apply {
            put("type", "chat_text")
            put("payload", JSONObject().put("text", trimmed))
        }

        val sent = webSocket?.send(payload.toString()) ?: false
        if (!sent) {
            Log.w(TAG, "Failed to send message — WebSocket not ready")
            messages.add(
                ChatMessage(
                    text = "Error: Sin conexión con el kernel.",
                    isUser = false,
                    isBlocked = true,
                    blockReason = "DISCONNECTED"
                )
            )
        }
    }

    fun approveVault(key: String) {
        val payload = JSONObject().apply {
            put("type", "vault_auth")
            put("key", key)
            put("approved", true)
        }
        webSocket?.send(payload.toString())
        pendingVaultKey.value = null
    }

    fun denyVault() {
        pendingVaultKey.value = null
    }

    // ── TTS Playback ────────────────────────────────────────────

    private fun playBase64Audio(b64: String) {
        try {
            val audioData = Base64.decode(b64, Base64.DEFAULT)
            // Write to temp file — MediaPlayer requires file or URI
            val file = File.createTempFile("ethos_tts_", ".mp3")
            file.deleteOnExit()
            file.writeBytes(audioData)
            tempAudioFile = file

            mediaPlayer?.release()
            mediaPlayer = MediaPlayer().apply {
                setDataSource(file.absolutePath)
                setOnPreparedListener {
                    isSpeaking.value = true
                    it.start()
                }
                setOnCompletionListener {
                    isSpeaking.value = false
                    it.release()
                    mediaPlayer = null
                    file.delete()
                }
                setOnErrorListener { _, what, extra ->
                    Log.e(TAG, "MediaPlayer error: what=$what extra=$extra")
                    isSpeaking.value = false
                    true
                }
                prepareAsync()
            }
        } catch (e: Exception) {
            Log.e(TAG, "TTS playback error", e)
            isSpeaking.value = false
        }
    }

    override fun onCleared() {
        super.onCleared()
        mediaPlayer?.release()
        mediaPlayer = null
        tempAudioFile?.delete()
        webSocket?.close(1000, "ViewModel cleared")
    }
}
