package com.ethos.nomad.ui

import androidx.compose.runtime.mutableStateListOf
import androidx.lifecycle.ViewModel
import okhttp3.*
import org.json.JSONObject
import android.util.Log

data class ChatMessage(
    val text: String,
    val isUser: Boolean,
    val timestamp: Long = System.currentTimeMillis()
)

class ChatViewModel : ViewModel() {
    private val TAG = "ChatViewModel"
    private val client = OkHttpClient()
    private var webSocket: WebSocket? = null
    
    val messages = mutableStateListOf<ChatMessage>()
    
    init {
        connect()
    }
    
    private fun connect() {
        val request = Request.Builder()
            .url("ws://10.0.2.2:8000/ws/chat")
            .build()
            
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(webSocket: WebSocket, response: Response) {
                Log.d(TAG, "Chat WebSocket Connected")
            }
            
            override fun onMessage(webSocket: WebSocket, text: String) {
                try {
                    val json = JSONObject(text)
                    val type = json.optString("type")
                    
                    when (type) {
                        "chat_text" -> {
                            val msg = json.optString("text")
                            if (msg.isNotEmpty()) {
                                addMessage(msg, false)
                            }
                        }
                        "done" -> {
                            // Optionally handle completion / thinking state
                        }
                        "metadata" -> {
                            // Future: Update agentic status (ethics score, risk)
                        }
                    }
                } catch (e: Exception) {
                    Log.e(TAG, "Error parsing message: $text", e)
                }
            }
            
            override fun onFailure(webSocket: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket Failure", t)
                // Implement retry logic if needed
            }
        })
    }
    
    fun sendMessage(text: String) {
        if (text.isBlank()) return
        
        val payload = JSONObject().apply {
            put("type", "chat_text")
            put("payload", JSONObject().put("text", text))
        }
        
        if (webSocket?.send(payload.toString()) == true) {
            addMessage(text, true)
        }
    }
    
    private fun addMessage(text: String, isUser: Boolean) {
        // Run on UI thread via state list
        messages.add(ChatMessage(text, isUser))
    }
    
    override fun onCleared() {
        super.onCleared()
        webSocket?.close(1000, "ViewModel cleared")
    }
}
