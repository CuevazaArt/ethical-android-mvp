package com.ethos.nomad

import android.app.Service
import android.content.Intent
import android.os.IBinder
import android.util.Log

class NomadService : Service() {

    private val TAG = "NomadService"

    override fun onCreate() {
        super.onCreate()
        Log.d(TAG, "Nomad Foreground Service Created")
        // TODO: Initialize Foreground Notification
        // TODO: Initialize OkHttp WebSocket Client
        // TODO: Initialize AudioRecord
    }

    override fun onStartCommand(intent: Intent?, flags: Int, startId: Int): Int {
        Log.d(TAG, "Nomad Foreground Service Started")
        // Return START_STICKY so the service restarts if killed
        return START_STICKY
    }

    override fun onBind(intent: Intent?): IBinder? {
        return null // We don't need IPC binding yet
    }

    override fun onDestroy() {
        super.onDestroy()
        Log.d(TAG, "Nomad Foreground Service Destroyed")
        // TODO: Clean up WebSockets and AudioRecord
    }
}
