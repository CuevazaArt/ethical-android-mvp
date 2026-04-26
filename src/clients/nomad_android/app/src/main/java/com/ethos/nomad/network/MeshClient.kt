// Copyright 2026 Juan Cuevaz / Mos Ex Machina
// Licensed under the Business Source License 1.1
// See LICENSE_BSL file for details.
package com.ethos.nomad.network

import android.content.Context
import android.util.Log
import com.ethos.nomad.audio.AudioStreamer
import com.ethos.nomad.hardware.NodeProfiler
import kotlinx.coroutines.CoroutineScope
import kotlinx.coroutines.Dispatchers
import kotlinx.coroutines.Job
import kotlinx.coroutines.SupervisorJob
import kotlinx.coroutines.cancel
import kotlinx.coroutines.delay
import kotlinx.coroutines.flow.Flow
import kotlinx.coroutines.launch
import okhttp3.OkHttpClient
import okhttp3.Request
import okhttp3.Response
import okhttp3.WebSocket
import okhttp3.WebSocketListener
import okio.ByteString
import okio.ByteString.Companion.toByteString
import java.nio.ByteBuffer
import java.nio.ByteOrder
import java.util.concurrent.TimeUnit
import java.util.concurrent.atomic.AtomicLong

private const val TAG = "MeshClient"
private const val PROTOCOL_VERSION = "1.0"
private const val TELEMETRY_INTERVAL_MS = 5_000L

/**
 * MeshClient
 *
 * Manages the WebSocket connection from the Android Nomad node to the Ethos Kernel.
 * Responsible for:
 *   1. Opening and maintaining the WebSocket connection to `ws://ip:port/ws/mesh`.
 *   2. Sending periodic [TelemetryPayload] heartbeats every 5 seconds.
 *   3. Streaming raw PCM audio chunks as binary [AudioChunkPayload] frames.
 *
 * Wire format for audio frames (per mesh_protocol_v1.md):
 *   [ 4 bytes: header_length uint32 LE ][ header_length bytes: JSON ][ PCM bytes ]
 */
class MeshClient(private val context: Context) {

    private val client: OkHttpClient = OkHttpClient.Builder()
        .pingInterval(10, TimeUnit.SECONDS)
        .connectTimeout(10, TimeUnit.SECONDS)
        .readTimeout(0, TimeUnit.SECONDS)  // Keep-alive; no read timeout.
        .build()

    private var webSocket: WebSocket? = null
    private val scope = CoroutineScope(SupervisorJob() + Dispatchers.IO)

    // Monotonically increasing audio sequence number, resets on reconnect.
    private val audioSeq = AtomicLong(0L)

    private var telemetryJob: Job? = null
    private var audioJob: Job? = null

    // ── Connection ────────────────────────────────────────────────────────────

    /**
     * Opens the WebSocket connection to `ws://ip:port/ws/mesh`.
     * Non-blocking; the handshake happens asynchronously.
     */
    fun connect(ip: String, port: Int) {
        audioSeq.set(0L)
        val url = "ws://$ip:$port/ws/mesh"
        Log.i(TAG, "Connecting to $url")

        val request = Request.Builder().url(url).build()
        webSocket = client.newWebSocket(request, object : WebSocketListener() {
            override fun onOpen(ws: WebSocket, response: Response) {
                Log.i(TAG, "WebSocket opened — $url")
            }

            override fun onMessage(ws: WebSocket, text: String) {
                Log.d(TAG, "← $text")
            }

            override fun onFailure(ws: WebSocket, t: Throwable, response: Response?) {
                Log.e(TAG, "WebSocket failure: ${t.message}")
            }

            override fun onClosed(ws: WebSocket, code: Int, reason: String) {
                Log.i(TAG, "WebSocket closed [$code] $reason")
            }
        })
    }

    // ── Telemetry ─────────────────────────────────────────────────────────────

    /**
     * Launches a coroutine that sends a [TelemetryPayload] every 5 seconds.
     *
     * @param profiler  NodeProfiler used to read hardware vitals.
     * @param deviceId  Stable device identifier matching DiscoveryPayload.
     */
    fun startTelemetryLoop(profiler: NodeProfiler, deviceId: String) {
        telemetryJob?.cancel()
        telemetryJob = scope.launch {
            while (true) {
                val ws = webSocket
                if (ws != null) {
                    val data = profiler.snapshot(context)
                    val json = buildTelemetryJson(deviceId, data)
                    val sent = ws.send(json)
                    if (sent) {
                        Log.d(TAG, "→ telemetry: battery=${data.batteryLevel} ram=${data.availableRamMb}MB")
                    } else {
                        Log.w(TAG, "Telemetry send failed — WebSocket not ready")
                    }
                }
                delay(TELEMETRY_INTERVAL_MS)
            }
        }
    }

    /**
     * Builds a `TelemetryPayload` JSON string from [NodeProfiler] data.
     * Manual construction avoids a Gson/Moshi dependency for this simple schema.
     */
    private fun buildTelemetryJson(deviceId: String, data: com.ethos.nomad.hardware.TelemetryData): String {
        val batteryTempStr = data.batteryTemperatureC?.toString() ?: "null"
        val cpuTempStr     = data.cpuTemperatureC?.toString()     ?: "null"
        return """{"protocol_version":"$PROTOCOL_VERSION","type":"telemetry","device_id":"$deviceId","timestamp_ms":${System.currentTimeMillis()},"battery":{"level":${data.batteryLevel},"is_charging":${data.isCharging},"temperature_c":$batteryTempStr},"cpu":{"temperature_c":$cpuTempStr},"memory":{"available_mb":${data.availableRamMb},"total_mb":${data.totalRamMb}}}"""
    }

    // ── Audio Streaming ───────────────────────────────────────────────────────

    /**
     * Collects [audioFlow] and sends each PCM chunk as a binary WebSocket frame.
     *
     * Binary frame layout (Little-Endian):
     * ```
     * [ 4 bytes: header_len uint32 LE ][ header_len bytes: JSON ][ PCM bytes ]
     * ```
     *
     * @param audioFlow  Cold [Flow] produced by [AudioStreamer.start].
     * @param deviceId   Stable device identifier matching DiscoveryPayload.
     */
    fun streamAudio(audioFlow: Flow<ByteArray>, deviceId: String) {
        audioJob?.cancel()
        audioJob = scope.launch {
            audioFlow.collect { pcm ->
                val ws = webSocket ?: return@collect
                val seq = audioSeq.getAndIncrement()
                val frame = buildAudioFrame(deviceId, seq, pcm)
                val sent = ws.send(frame)
                if (!sent) {
                    Log.w(TAG, "Audio frame #$seq send failed — WebSocket not ready")
                }
            }
        }
    }

    /**
     * Assembles the binary audio frame according to the mesh_protocol_v1 wire format.
     */
    private fun buildAudioFrame(deviceId: String, seq: Long, pcm: ByteArray): ByteString {
        val header = """{"protocol_version":"$PROTOCOL_VERSION","type":"audio_chunk","device_id":"$deviceId","seq":$seq,"sample_rate_hz":${AudioStreamer.SAMPLE_RATE_HZ},"channels":1,"bits_per_sample":16,"pcm_length_bytes":${pcm.size},"timestamp_ms":${System.currentTimeMillis()}}"""
        val headerBytes = header.toByteArray(Charsets.UTF_8)

        // 4-byte Little-Endian header length prefix
        val lenPrefix = ByteBuffer.allocate(4)
            .order(ByteOrder.LITTLE_ENDIAN)
            .putInt(headerBytes.size)
            .array()

        val frame = lenPrefix + headerBytes + pcm
        return frame.toByteString()
    }

    // ── Lifecycle ─────────────────────────────────────────────────────────────

    /**
     * Cancels all running coroutines and closes the WebSocket gracefully.
     */
    fun disconnect() {
        telemetryJob?.cancel()
        audioJob?.cancel()
        webSocket?.close(1000, "MeshClient disconnected")
        webSocket = null
        scope.cancel()
        Log.i(TAG, "MeshClient disconnected")
    }
}
