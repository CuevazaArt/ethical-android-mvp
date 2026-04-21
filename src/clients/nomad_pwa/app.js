/**
 * Nomad PWA Bridge Client (Bloque F.1: Antigravity)
 * Handles UI state and prepares the WebSocket architecture for F.2/F.3/F.4 blocks.
 */

const UI = {
    orb: document.getElementById('affect-orb'),
    statusText: document.getElementById('socket-text'),
    statusDot: document.querySelector('.status-indicator'),
    btnConnect: document.getElementById('btn-connect'),
    btnStream: document.getElementById('btn-stream'),
    batterySpan: document.getElementById('battery-level'),
    transcript: document.getElementById('charm-transcript'),
    videoElement: document.getElementById('hidden-video'),
    // NEW BLOCK 13.1 elements
    chatInput: document.getElementById('chat-input'),
    btnSend: document.getElementById('btn-send'),
    telBat: document.getElementById('tel-bat'),
    telTemp: document.getElementById('tel-temp'),
    telKin: document.getElementById('tel-kin'),
    telAud: document.getElementById('tel-aud'),
};

let wsChat = null;
let wsNomad = null;
let isConnected = false;
/** @type {number|null} performance.now() when last bridge ping was sent (S.1.1 RTT) */
let nomadBridgePingT0 = null;
/** @type {ReturnType<typeof setInterval>|null} */
let nomadPingIntervalId = null;
/** @type {ReturnType<typeof setInterval>|null} */
let nomadHeartbeatIntervalId = null;

const NOMAD_LAST_GOOD_HOST_KEY = 'nomad:last_good_host';

function _wsProtocol() {
    return window.location.protocol === 'https:' ? 'wss:' : 'ws:';
}

function _httpProtocol() {
    return window.location.protocol === 'https:' ? 'https:' : 'http:';
}

async function resolveKernelEndpointCandidates() {
    const candidates = [];
    const currentHost = window.location.hostname || '127.0.0.1';
    const currentPort = window.location.port || '8765';
    const wsProto = _wsProtocol();
    const baseCurrent = `${wsProto}//${currentHost}:${currentPort}`;

    candidates.push({
        host: currentHost,
        chat_ws: `${baseCurrent}/ws/chat`,
        nomad_ws: `${baseCurrent}/ws/nomad`,
    });

    const cachedHost = localStorage.getItem(NOMAD_LAST_GOOD_HOST_KEY);
    if (cachedHost && cachedHost !== currentHost) {
        const baseCached = `${wsProto}//${cachedHost}:${currentPort}`;
        candidates.push({
            host: cachedHost,
            chat_ws: `${baseCached}/ws/chat`,
            nomad_ws: `${baseCached}/ws/nomad`,
        });
    }

    try {
        const discoveryUrl = `${_httpProtocol()}//${currentHost}:${currentPort}/discovery/nomad`;
        const resp = await fetch(discoveryUrl, { method: 'GET', cache: 'no-store' });
        if (resp.ok) {
            const payload = await resp.json();
            const fromApi = Array.isArray(payload?.candidates) ? payload.candidates : [];
            fromApi.forEach((row) => {
                if (!row || typeof row !== 'object') return;
                if (!row.chat_ws || !row.nomad_ws) return;
                const already = candidates.some((c) => c.chat_ws === row.chat_ws);
                if (!already) {
                    candidates.push({
                        host: row.host || currentHost,
                        chat_ws: row.chat_ws,
                        nomad_ws: row.nomad_ws,
                    });
                }
            });
        }
    } catch (_) {
        // Keep local fallback candidates when discovery endpoint is unavailable.
    }

    return candidates;
}

function connectPair(candidate) {
    return new Promise((resolve, reject) => {
        let settled = false;
        
        // Bloque 13.1 Resilience: Timeout to prevent "Trying..." hang if firewall drops packets
        const timeoutId = setTimeout(() => {
            cleanupAndReject(new Error('Connection timed out. Checking firewall/network...'));
        }, 8000);

        console.log(`Nomad: Attempting WS handshake at ${candidate.host}`);
        
        // We create nomad first. If chat fails, we might still function via nomad relay.
        let nomad, chat;
        try {
            nomad = new WebSocket(candidate.nomad_ws);
            chat = new WebSocket(candidate.chat_ws);
        } catch (e) {
            return cleanupAndReject(new Error(`Browser blocked WS creation: ${e.message}`));
        }

        const cleanupAndReject = (err) => {
            if (settled) return;
            settled = true;
            clearTimeout(timeoutId);
            try { chat.close(); } catch (_) {}
            try { nomad.close(); } catch (_) {}
            reject(err);
        };

        let chatReady = false;
        let nomadReady = false;

        const maybeResolve = () => {
            if (settled) return;
            // For now, we require both for full functionality. 
            // In future, nomad relay could allow chat=null.
            if (chatReady && nomadReady) {
                settled = true;
                clearTimeout(timeoutId);
                resolve({ chat, nomad, host: candidate.host });
            }
        };

        chat.onopen = () => { console.log("Nomad: Chat WS Open"); chatReady = true; maybeResolve(); };
        nomad.onopen = () => { console.log("Nomad: Sensor WS Open"); nomadReady = true; maybeResolve(); };
        
        chat.onerror = (e) => {
            console.error("Nomad: Chat WS Error", e);
            cleanupAndReject(new Error('Chat WebSocket (ws/chat) failed. Check Firewall.'));
        };
        nomad.onerror = (e) => {
            console.error("Nomad: Sensor WS Error", e);
            cleanupAndReject(new Error('Sensor WebSocket (ws/nomad) failed. Check Firewall.'));
        };
        
        chat.onclose = () => { if (!settled) cleanupAndReject(new Error('Chat WS closed by server/router.')); };
        nomad.onclose = () => { if (!settled) cleanupAndReject(new Error('Sensor WS closed by server/router.')); };
    });
}

/**
 * Reconnection Logic (Bloque F.4: Claude)
 */
let reconnectAttempts = 0;
const MAX_RECONNECT_ATTEMPTS = 5;
const RECONNECT_DELAY_BASE = 2000;

/**
 * Battery & Kinetic Telemetry (Replaced Temp due to browser security)
 */
let lastKineticPulse = 0;
let lastBatteryLevel = null;

if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
        lastBatteryLevel = battery.level;
        const sendBat = () => {
            try {
                const level = Math.round(battery.level * 100);
                UI.batterySpan.innerText = `${level}%`;
                
                if(wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                    // Proxy for 'Temperature' (browser block workaround): High drain scale
                    let tempProxy = 40 + (1.0 - battery.level) * 10; 
                    if (!Number.isFinite(tempProxy)) tempProxy = 40.0;
                    
                    wsNomad.send(JSON.stringify({ 
                        type: "telemetry", 
                        payload: { 
                            battery: battery.level,
                            is_charging: battery.charging,
                            temp: tempProxy // Simulated thermal state based on drain
                        } 
                    }));
                }
            } catch (e) {
                console.warn("Nomad: Battery telemetry error", e);
            }
        };
        battery.addEventListener('levelchange', sendBat);
        battery.addEventListener('chargingchange', sendBat);
        sendBat();
    }).catch((err) => {
        console.warn('Battery API unavailable', err);
    });
}

// Bloque S.2.2: Screen Wake Lock (prevents disconnection when screen dims)
let wakeLock = null;
async function requestWakeLock() {
    try {
        if ('wakeLock' in navigator) {
            wakeLock = await navigator.wakeLock.request('screen');
            console.log('Nomad: Wake Lock acquired.');
            wakeLock.addEventListener('release', () => {
                console.log('Nomad: Wake Lock released.');
            });
        }
    } catch (err) {
        console.warn(`Nomad: Wake Lock failed: ${err.name}, ${err.message}`);
    }
}

window.addEventListener('deviceorientation', (event) => {
    if(wsNomad && wsNomad.readyState === WebSocket.OPEN) {
        wsNomad.send(JSON.stringify({
            type: "telemetry",
            payload: {
                orientation: {
                    alpha: event.alpha, // Z-axis compass
                    beta: event.beta,   // X-axis tilt
                    gamma: event.gamma  // Y-axis roll
                }
            }
        }));
    }
});

window.addEventListener('devicemotion', (event) => {
    try {
        if(wsNomad && wsNomad.readyState === WebSocket.OPEN) {
            let acc = event.acceleration;
            if(acc) {
                let magnitude = Math.sqrt((acc.x||0)**2 + (acc.y||0)**2 + (acc.z||0)**2);
                if (!Number.isFinite(magnitude)) magnitude = 0.0;
                
                let now = Date.now();
                
                // Phase 12 Hardening: High-intensity impact detection
                // Phase 12 Hardening: Enhanced sensitivity (tuned to 1.1 from user feedback)
                if(magnitude > 1.1) { 
                    wsNomad.send(JSON.stringify({ type: "telemetry", payload: { kinetics: magnitude } }));
                    lastKineticPulse = now;
                } else if(now - lastKineticPulse > 2000) {
                    // Send idle heartbeat with 0 kinetics to settle the dashboard lóbulo
                    wsNomad.send(JSON.stringify({ type: "telemetry", payload: { kinetics: 0, heartbeat: true } }));
                    lastKineticPulse = now;
                }
            }
        }
    } catch (e) {
        console.warn("Nomad: DeviceMotion telemetry fault", e);
    }
});

/**
 * Update the visual state of the application based on backend affectations/charms.
 * Expected states: 'calm', 'alert', 'active'
 */
function setAppAffectState(state) {
    document.body.className = ''; // reset 
    if (state && state !== 'calm') {
        document.body.classList.add(`state-${state}`);
    }
}

/**
 * Handle initial Backend Connection
 */
async function connectKernel() {
    // Bloque 13.1 Security: Check for Secure Context (HTTPS or Localhost)
    // Sensors (Camera/Mic) are blocked by modern browsers on insecure origins.
    if (!window.isSecureContext) {
        console.warn("Nomad: Not running in a Secure Context. Sensors may be blocked.");
        // We show a one-time non-blocking warning (or log it)
        UI.statusText.innerText = "Insecure Context (Sensors Limited)";
    } else {
        UI.statusText.innerText = "Connecting...";
    }
    
    console.log("Nomad: Initializing connection sequence...");

    try {
        const candidates = await resolveKernelEndpointCandidates();
        console.log("Nomad: Candidates identified:", candidates);
        
        let connected = null;
        let lastErr = 'None';
        
        for (const c of candidates) {
            UI.statusText.innerText = `Trying ${c.host}...`;
            try {
                // Bloque 13.1 Resilience: Attempt to connect to the pair.
                connected = await connectPair(c);
                console.log(`Nomad: Successfully connected to ${c.host}`);
                
                // Bloque S.2.2: Acquire Wake Lock upon successful connection
                requestWakeLock();
                break;
            } catch (err) {
                console.warn(`Nomad: Candidate ${c.host} failed:`, err);
                lastErr = err.message || err.toString();
            }
        }
        
        if (!connected) {
            throw new Error(`Connection failed across all candidates. Last error: ${lastErr}`);
        }

        wsChat = connected.chat;
        wsNomad = connected.nomad;
        
        try {
            localStorage.setItem(NOMAD_LAST_GOOD_HOST_KEY, connected.host || '');
        } catch (_) {}
        
        // Bloque 13.1 Resilience: sockets are ALREADY open because connectPair resolved.
        // We trigger the UI transition immediately.
        isConnected = true;
        UI.statusDot.classList.add('connected');
        UI.statusText.innerText = "Kernel Synced";
        UI.transcript.innerText = "Ready. Waiting for sensors...";
        UI.transcript.classList.remove('placeholder');
        
        UI.btnConnect.disabled = true;
        UI.btnConnect.innerText = "Connected";
        
        // Enable the streaming button for Cursor (Block F.2)
        UI.btnStream.disabled = false;
        UI.btnStream.classList.remove('inactive');

        // Note: wsChat.onopen would be too late here, so we skip it.

        wsChat.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                // Bloque 13.1: Native response handling from Ethos Kernel
                if (data.event_type === "turn_finished") {
                    const msg = data.payload?.response?.message || "";
                    if (msg) {
                        UI.transcript.innerText = msg;
                        UI.transcript.classList.remove('placeholder');
                    }
                }
            } catch (e) {
                console.warn("Nomad: Chat message parse error", e);
            }
        };

        wsChat.onclose = () => {
            isConnected = false;
            UI.statusDot.classList.remove('connected');
            UI.statusText.innerText = "Disconnected";
            setAppAffectState('calm');
            
            UI.btnConnect.disabled = false;
            UI.btnConnect.innerText = "Reconnect";
            UI.btnStream.disabled = true;
            UI.btnStream.classList.add('inactive');

            // Trigger reconnection (Claude's backoff)
            if (reconnectAttempts < MAX_RECONNECT_ATTEMPTS) {
                const delay = RECONNECT_DELAY_BASE * Math.pow(2, reconnectAttempts);
                UI.statusText.innerText = `Retrying in ${delay / 1000}s...`;
                setTimeout(() => {
                    reconnectAttempts++;
                    connectKernel();
                }, delay);
            }
        };

        wsNomad.onopen = () => { 
            console.log('Nomad Sensory Bridge established');
            if (nomadPingIntervalId != null) {
                try { clearInterval(nomadPingIntervalId); } catch (e) { /* ignore */ }
                nomadPingIntervalId = null;
            }
            if (nomadHeartbeatIntervalId != null) {
                try { clearInterval(nomadHeartbeatIntervalId); } catch (e) { /* ignore */ }
                nomadHeartbeatIntervalId = null;
            }
            // Heavy Heartbeat (Fase 12.2)
            nomadHeartbeatIntervalId = setInterval(() => {
               try {
                   if(wsNomad.readyState === WebSocket.OPEN) {
                       wsNomad.send(JSON.stringify({ type: "telemetry", payload: { heartbeat: true } }));
                   }
               } catch (e) {
                   console.warn('Nomad heartbeat send failed', e);
               }
            }, 15000);
            // S.1.1 — LAN RTT / keepalive (pairs with server `pong` in nomad_bridge.py)
            nomadPingIntervalId = setInterval(() => {
                try {
                    if (wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                        nomadBridgePingT0 = performance.now();
                        wsNomad.send(JSON.stringify({ type: "ping", payload: {} }));
                    }
                } catch (e) {
                    console.warn('Nomad bridge ping failed', e);
                }
            }, 10000);
        };

        wsNomad.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'pong' && msg.payload && nomadBridgePingT0 != null) {
                    const rttMs = Math.round(performance.now() - nomadBridgePingT0);
                    nomadBridgePingT0 = null;
                    console.debug('Nomad bridge RTT (ms):', rttMs);
                    if (UI.nomadRtt) {
                        UI.nomadRtt.textContent = `${rttMs} ms`;
                    }
                } else if (msg.type === 'charm_feedback') {
                    console.debug('Nomad charm_feedback', msg.payload);
                }
            } catch (e) {
                console.warn('Nomad WS message parse error', e);
            }
        };

        wsNomad.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'charm_feedback') {
                    const payload = msg.payload;
                    // Support standard voice nudges from the bridge (S.2.1)
                    if (payload.type === 'kernel_voice' || payload.text) {
                        const text = payload.text || payload.content;
                        UI.transcript.innerText = `[Proxied] Kernel: ${text}`;
                        if ('speechSynthesis' in window) {
                            const utterance = new SpeechSynthesisUtterance(text);
                            window.speechSynthesis.speak(utterance);
                        }
                    }
                    if (payload.type === 'haptic_feedback' || payload.haptics) {
                        const pattern = payload.haptics || [200, 100, 200];
                        if (navigator.vibrate) navigator.vibrate(pattern);
                    }
                }
            } catch (e) {
                console.error("Nomad Bridge message error", e);
            }
        };

    } catch (e) {
        alert(`Connectivity Error: ${e.message || e}\n\nTroubleshoot:\n1. Ensure you are on the SAME Wi-Fi.\n2. Allow port 8765 in Windows Firewall (PC).\n3. Keep mobile browser 'Shields' off for this IP.`);
        UI.statusText.innerText = "Error";
    }
}

// Event Listeners with Safe-Check (Boy Scout Hardening)
if (UI.btnConnect) {
 /**
 * Dispatch typed message to the kernel via /ws/chat
 */
function sendNomadChatMessage() {
    const text = (UI.chatInput.value || "").trim();
    if (!text || !wsChat || wsChat.readyState !== WebSocket.OPEN) return;

    wsChat.send(JSON.stringify({ text }));
    UI.transcript.innerText = `...`; // Thinking state
    UI.chatInput.value = "";
}

// ── INIT ───────────────────────────────────────────────────────────────────
UI.btnConnect.addEventListener('click', connectKernel);
UI.btnStream.addEventListener('click', () => {
    if (typeof startSensors === 'function') startSensors();
    UI.btnStream.disabled = true;
    UI.btnStream.innerText = "STREAMING";
});

UI.btnSend.addEventListener('click', sendNomadChatMessage);
UI.chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendNomadChatMessage();
});
}

// Expose a function to scale the orb based on audio volume
window.updateOrbScale = function(volume) {
    // Volume is typically between 0 and 1
    const scale = 1 + (volume * 1.5);
    UI.orb.style.transform = `scale(${scale})`;
};

// Application Installation (PWA Service Worker)
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    // Prevent default mini-infobar
    e.preventDefault();
    deferredPrompt = e;
});

UI.btnInstall.addEventListener('click', async () => {
    if (deferredPrompt) {
        deferredPrompt.prompt();
        const { outcome } = await deferredPrompt.userChoice;
        if (outcome === 'accepted') {
            UI.btnInstall.style.display = 'none';
        }
        deferredPrompt = null;
    } else {
        alert("Modo Manual:\n1. Toca los tres puntos (Menú) de tu navegador.\n2. Toca 'Instalar Aplicación' o 'Añadir a pantalla de inicio'.\n¡Esto evitará que el sistema cierre la cámara!");
    }
});

/**
 * Dispatch typed message to the kernel via /ws/chat
 */
function sendNomadChatMessage() {
    const text = (UI.chatInput.value || "").trim();
    if (!text || !wsChat || wsChat.readyState !== WebSocket.OPEN) return;

    wsChat.send(JSON.stringify({ text }));
    UI.transcript.innerText = `...`; // Thinking state
    UI.chatInput.classList.add('sending');
    UI.chatInput.value = "";
    setTimeout(() => UI.chatInput.classList.remove('sending'), 500);
}

// ── Sensory HUD Updates ──────────────────────────────────────────────────
function updateHud(type, val) {
    try {
        if (type === 'bat' && UI.telBat) UI.telBat.innerText = `${Math.round(val * 100)}%`;
        if (type === 'temp' && UI.telTemp) UI.telTemp.innerText = `${Math.round(val)}°`;
        if (type === 'kin' && UI.telKin) UI.telKin.innerText = val.toFixed(1);
        if (type === 'aud' && UI.telAud) UI.telAud.innerText = val.toFixed(2);
    } catch(_) {}
}

// ── INIT ───────────────────────────────────────────────────────────────────
if (UI.btnConnect) UI.btnConnect.addEventListener('click', connectKernel);
if (UI.btnStream)  UI.btnStream.addEventListener('click', () => {
    if (typeof startSensors === 'function') startSensors();
    UI.btnStream.disabled = true;
    UI.btnStream.innerText = "STREAMING";
});
if (UI.btnSend)    UI.btnSend.addEventListener('click', sendNomadChatMessage);
if (UI.chatInput)  UI.chatInput.addEventListener('keypress', (e) => {
    if (e.key === 'Enter') sendNomadChatMessage();
});

// Update battery in real-time if available
if ('getBattery' in navigator) {
    navigator.getBattery().then(bat => {
        const up = () => updateHud('bat', bat.level);
        bat.addEventListener('levelchange', up);
        up();
    });
}

// Global Orb Scale
window.updateOrbScale = function(volume) {
    if (!UI.orb) return;
    const s = 1 + (volume * 0.4);
    UI.orb.style.transform = `scale(${s})`;
    updateHud('aud', volume);
};

// ... existing SW registration ...
if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js?v=13.1.5')
            .then(reg => console.log('Nomad Service Worker registered', reg))
            .catch(err => console.error('SW block:', err));
    });
}

console.log("Nomad PWA V13.1.5 Initialized.");
