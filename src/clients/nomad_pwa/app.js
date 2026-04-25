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
    chatHistory: document.getElementById('chat-history'),
    chatInput: document.getElementById('chat-input'),
    btnSend: document.getElementById('btn-send'),
    videoElement: document.getElementById('hidden-video'),
    identityStrip: document.getElementById('identity-strip'),
    btnUiMode: document.getElementById('btn-ui-mode'),
    btnInstall: document.getElementById('btn-install'),
    transcript: document.getElementById('charm-transcript'),
    telBat: document.getElementById('tel-bat'),
    telTemp: document.getElementById('tel-temp'),
    telKin: document.getElementById('tel-kin'),
    telAud: document.getElementById('tel-aud'),
    nomadRtt: document.getElementById('nomad-rtt'),
    ethicsHud: document.getElementById('ethics-hud'),
};

let wsChat = null;
let wsNomad = null;
let isConnected = false;
window.isEthosSpeaking = false;
window.currentEthosText = "";
window.currentAudioElement = null;

// ── TTS helper — español garantizado ──────────────────────────────────────
// Los browsers cargan voces de forma asíncrona; llamar getVoices() en el
// primer frame devuelve [] y el browser elige la voz por defecto (puede ser IT).
// Esta función espera a que las voces estén listas antes de hablar.
function _speak(text) {
    if (!('speechSynthesis' in window) || !text.trim()) return;
    window.speechSynthesis.cancel();
    const utter = new SpeechSynthesisUtterance(text.replace(/[*_~`#>\-]/g, '').trim());
    utter.lang = 'es-MX';
    window.currentEthosText = text.toLowerCase().replace(/[^a-záéíóúüñ\s]/g, '');
    utter.onstart = () => { window.isEthosSpeaking = true; if (UI.orb) UI.orb.classList.add('speaking'); };
    utter.onend   = () => { window.isEthosSpeaking = false; if (UI.orb) UI.orb.classList.remove('speaking'); };
    utter.onerror = () => { window.isEthosSpeaking = false; if (UI.orb) UI.orb.classList.remove('speaking'); };

    function _pickVoiceAndSpeak() {
        const voices = window.speechSynthesis.getVoices();
        // Preferencia: es-MX → cualquier es-* (excluye it-, fr-, etc)
        const esVoice = voices.find(v => v.lang === 'es-MX')
                     || voices.find(v => v.lang === 'es-US')
                     || voices.find(v => v.lang === 'es-ES')
                     || voices.find(v => v.lang.startsWith('es'));
        if (esVoice) utter.voice = esVoice;
        // Si no hay ninguna voz española, al menos forzar lang y dejar que el
        // browser sintetice sin asignar voice (mejor que italiano por defecto).
        window.speechSynthesis.speak(utter);
    }

    const voices = window.speechSynthesis.getVoices();
    if (voices.length > 0) {
        _pickVoiceAndSpeak();
    } else {
        window.speechSynthesis.onvoiceschanged = () => {
            _pickVoiceAndSpeak();
            window.speechSynthesis.onvoiceschanged = null;
        };
    }
}

// ── V2.52 Limbic System (Emotional Resonance) ───────────────────────────────
window.setAppAffectState = function(state) {
    document.body.classList.remove('state-alarm', 'state-alert', 'state-calm');
    document.body.classList.add(`state-${state}`);
};
// ─────────────────────────────────────────────────────────────────────────────
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
    const currentPort = window.location.port || '8000';
    const wsProto = _wsProtocol();
    const lanIp = currentHost;
    const baseCurrent = `${wsProto}//${lanIp}:${currentPort}`;
    
    console.log("Nomad: Forcing direct LAN candidate:", baseCurrent);

    candidates.push({
        host: lanIp,
        chat_ws: `${baseCurrent}/ws/chat`,
        nomad_ws: `${baseCurrent}/ws/nomad`,
    });





    try {
        const cachedHost = localStorage.getItem(NOMAD_LAST_GOOD_HOST_KEY);
        if (cachedHost && cachedHost !== currentHost) {
            const baseCached = `${wsProto}//${cachedHost}:${currentPort}`;
            candidates.push({
                host: cachedHost,
                chat_ws: `${baseCached}/ws/chat`,
                nomad_ws: `${baseCached}/ws/nomad`,
            });
        }
    } catch (e) {
        console.warn("Nomad: Cannot access localStorage:", e);
    }

    /*
    try {
        const currentHost = window.location.hostname || '127.0.0.1';
        const currentPort = window.location.port || '8765';
        const discoveryUrl = `${_httpProtocol()}//${currentHost}:${currentPort}/discovery/nomad`;
        const resp = await fetch(discoveryUrl, { method: 'GET', cache: 'no-store' });
        // ... (discovery logic disabled for LAN stabilization)
    } catch (_) {
        // Keep local fallback candidates when discovery endpoint is unavailable.
    }
    */



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
            console.log("Nomad: Attempting WebSocket connection to:", candidate.nomad_ws);
            nomad = new WebSocket(candidate.nomad_ws);
            chat = new WebSocket(candidate.chat_ws);
        } catch (wsErr) {
            alert("Error crítico al crear WebSocket: " + wsErr.message);
            reject(wsErr);
            return;
        }


        const cleanupAndReject = (err) => {
            if (settled) return;
            settled = true;
            clearTimeout(timeoutId);
            try { chat.close(); } catch (_) {}
            try { nomad.close(); } catch (_) {}
            alert("Conexión fallida: " + err.message);
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
            cleanupAndReject(new Error('Chat WebSocket (ws/chat) falló. Revisa el Firewall.'));
        };
        nomad.onerror = (e) => {
            console.error("Nomad: Sensor WS Error", e);
            cleanupAndReject(new Error('Sensor WebSocket (ws/nomad) falló. Revisa el Firewall.'));
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

/** Bloque 22.1: outbound chat while /ws/chat or relay path is briefly down (mobile 4G/5G). */
const OUTBOUND_CHAT_MAX = 48;
/** @type {string[]} */
let outboundChatBuffer = [];
/** @type {ReturnType<typeof setTimeout>|null} */
let reconnectTimerId = null;

function clearKernelReconnectTimer() {
    if (reconnectTimerId != null) {
        clearTimeout(reconnectTimerId);
        reconnectTimerId = null;
    }
}

function enqueueOutboundChat(text) {
    while (outboundChatBuffer.length >= OUTBOUND_CHAT_MAX) {
        outboundChatBuffer.shift();
    }
    outboundChatBuffer.push(text);
}

function trySendChatWsJSON(obj) {
    if (!wsChat || wsChat.readyState !== WebSocket.OPEN) return false;
    try {
        wsChat.send(JSON.stringify(obj));
        return true;
    } catch (e) {
        console.warn('Nomad: chat WS send failed', e);
        return false;
    }
}

function trySendNomadChatRelay(text) {
    if (!wsNomad || wsNomad.readyState !== WebSocket.OPEN) return false;
    try {
        wsNomad.send(JSON.stringify({ type: 'chat_text', payload: { text } }));
        return true;
    } catch (e) {
        console.warn('Nomad: chat_text relay send failed', e);
        return false;
    }
}

function flushOutboundChatBuffer() {
    while (outboundChatBuffer.length > 0) {
        const t = outboundChatBuffer[0];
        if (trySendChatWsJSON({ text: t })) {
            outboundChatBuffer.shift();
        } else if (trySendNomadChatRelay(t)) {
            outboundChatBuffer.shift();
        } else {
            break;
        }
    }
}

function scheduleKernelReconnect(reason) {
    if (reconnectTimerId != null) return;
    if (reconnectAttempts >= MAX_RECONNECT_ATTEMPTS) {
        if (UI.statusText) UI.statusText.innerText = 'Offline — tap Reconnect';
        return;
    }
    const delay = RECONNECT_DELAY_BASE * Math.pow(2, reconnectAttempts);
    if (UI.statusText) UI.statusText.innerText = `Disconnected (${reason}). Retry in ${delay / 1000}s…`;
    reconnectTimerId = setTimeout(() => {
        reconnectTimerId = null;
        reconnectAttempts += 1;
        connectKernel();
    }, delay);
}

function teardownKernelSockets() {
    clearKernelReconnectTimer();
    if (nomadPingIntervalId != null) {
        try { clearInterval(nomadPingIntervalId); } catch (_) { /* ignore */ }
        nomadPingIntervalId = null;
    }
    if (nomadHeartbeatIntervalId != null) {
        try { clearInterval(nomadHeartbeatIntervalId); } catch (_) { /* ignore */ }
        nomadHeartbeatIntervalId = null;
    }
    try { if (wsChat) wsChat.close(); } catch (_) { /* ignore */ }
    try { if (wsNomad) wsNomad.close(); } catch (_) { /* ignore */ }
    wsChat = null;
    wsNomad = null;
}

function nomadApplySendingUi(thinking) {
    if (thinking && UI.transcript) {
        UI.transcript.innerText = '...';
        UI.transcript.classList.remove('placeholder');
    }
    if (UI.chatInput) {
        UI.chatInput.value = '';
        UI.chatInput.classList.add('sending');
        setTimeout(() => {
            try { UI.chatInput.classList.remove('sending'); } catch (_) { /* ignore */ }
        }, 500);
    }
}

function sendNomadChatMessage() {
    const raw = UI.chatInput ? UI.chatInput.value : '';
    const text = (raw || '').trim();
    if (!text) return;

    // V2.45: Reset ethics HUD for the new turn
    if (UI.ethicsHud) UI.ethicsHud.style.display = 'none';

    if (trySendChatWsJSON({ text })) {
        appendChatMessage(text, 'user');
        nomadApplySendingUi(true);
        return;
    }
    if (trySendNomadChatRelay(text)) {
        appendChatMessage(text, 'user');
        nomadApplySendingUi(true);
        return;
    }
    enqueueOutboundChat(text);
    nomadApplySendingUi(false);
    if (UI.statusText) UI.statusText.innerText = 'Queued (waiting for link)…';
}

/** V2.45: Update the Ethics HUD with real-time context from a ``metadata`` WS event. */
const _CTX_COLORS = {
    'medical_emergency':   '#ff4444',
    'violent_crime':       '#ff6600',
    'minor_crime':         '#ffaa00',
    'hostile_interaction': '#cc44cc',
    'everyday_ethics':     '#44cc88',
    'safety_violation':    '#ff6600',
};
function _handleEthicalMetadata(msg) {
    const hud = document.getElementById('ethics-hud');
    if (!hud) return;
    const ctx     = msg.context                               || 'everyday_ethics';
    const verdict = (msg.evaluation && msg.evaluation.verdict) || 'Neutral';
    const urgency = (msg.signals   && msg.signals.urgency)     || 0;
    const risk    = (msg.signals   && msg.signals.risk)        || 0;
    if (!Number.isFinite(urgency) || !Number.isFinite(risk)) return;
    hud.style.borderColor = _CTX_COLORS[ctx] || '#888';
    hud.textContent = `⚖ ${ctx.replace(/_/g, ' ')} · ${verdict} · urg=${urgency.toFixed(2)} risk=${risk.toFixed(2)}`;
    hud.style.display = 'block';
}

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
                    if (UI.telTemp) UI.telTemp.textContent = tempProxy.toFixed(1) + '°';
                    if (UI.telBat) UI.telBat.textContent = `${level}%`;
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
                    if (UI.telKin) UI.telKin.textContent = magnitude.toFixed(1);
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
 * V2.45: Handle backend `metadata` event — show ethical context in HUD before tokens arrive.
 * Called synchronously before the first token, so users see context immediately.
 */
function _handleEthicalMetadata(data) {
    const hud = UI.ethicsHud;
    if (!hud) return;

    const ctx     = (data.context || 'everyday_ethics').replace(/_/g, ' ');
    const verdict = data.evaluation ? data.evaluation.verdict || 'Neutral' : 'Neutral';
    const urgency = (data.signals && Number.isFinite(data.signals.urgency)) ? data.signals.urgency : 0;
    const risk    = (data.signals && Number.isFinite(data.signals.risk))    ? data.signals.risk    : 0;

    // Color-code border by context severity
    const ctxColors = {
        'medical emergency': '#e05252',
        'violent crime':     '#e07832',
        'minor crime':       '#d4c14a',
        'hostile interaction':'#c06adb',
        'everyday ethics':   '#4adb8a',
    };
    const color = ctxColors[ctx] || '#6a8adb';

    hud.style.borderColor = color;
    hud.style.display     = 'block';
    hud.innerHTML = (
        `<span style="color:${color}">⚖</span> ` +
        `<strong>${ctx}</strong> · ` +
        `${verdict} · ` +
        `urg <span style="color:${urgency > 0.6 ? '#e05252' : '#ccc'}">${urgency.toFixed(2)}</span> · ` +
        `risk <span style="color:${risk > 0.6 ? '#e05252' : '#ccc'}">${risk.toFixed(2)}</span>`
    );
}

/**
 * Update the visual state of the application based on backend affectations/charms.
 * Expected states: 'calm', 'alert', 'active'
 */
function setAppAffectState(state) {
    const textFocus = document.body.classList.contains('nomad-text-focus');
    document.body.className = '';
    if (textFocus) {
        document.body.classList.add('nomad-text-focus');
    }
    if (state && state !== 'calm') {
        document.body.classList.add(`state-${state}`);
    }
}

/** Bloque 22.3 — PAD / sigma from gestalt dict (server ``sync_identity_v1`` envelope). */
function applyGestaltPad(gestalt) {
    if (!gestalt || typeof gestalt !== 'object') return;
    const pad = gestalt.pad_state;
    if (Array.isArray(pad) && pad.length >= 3) {
        const to01 = (raw) => {
            const x = Number(raw);
            if (!Number.isFinite(x)) return 0;
            if (x < 0 || x > 1) return Math.max(0, Math.min(1, (x + 1) / 2));
            return Math.max(0, Math.min(1, x));
        };
        const p = to01(pad[0]);
        const a = to01(pad[1]);
        const d = to01(pad[2]);
        if (Number.isFinite(p)) {
            document.documentElement.style.setProperty('--pad-p', String(p));
            document.documentElement.style.setProperty('--pad-pleasure', String(p));
        }
        if (Number.isFinite(a)) {
            document.documentElement.style.setProperty('--pad-a', String(a));
            document.documentElement.style.setProperty('--pad-arousal', String(a));
        }
        if (Number.isFinite(d)) {
            document.documentElement.style.setProperty('--pad-d', String(d));
            document.documentElement.style.setProperty('--pad-dominance', String(d));
        }
        let axis = 'pleasure';
        if (a >= p && a >= d) axis = 'arousal';
        else if (d >= p && d >= a) axis = 'dominance';
        if (UI.orb && !document.body.classList.contains('nomad-text-focus')) {
            UI.orb.setAttribute('data-pad-axis', axis);
        }
    }
    const sigma = Number(gestalt.sigma);
    if (Number.isFinite(sigma)) {
        document.documentElement.style.setProperty('--gestalt-sigma', String(sigma));
        if (sigma > 0.72) setAppAffectState('alert');
        else if (sigma < 0.28) setAppAffectState('active');
        else setAppAffectState('calm');
    }
}

/** Bloque 22.2 — align UI with kernel ``[SYNC_IDENTITY]`` envelope (payload + top-level fields). */
function applySyncIdentity(data) {
    if (!data || typeof data !== 'object') return;
    const inner = data.payload && typeof data.payload === 'object' ? data.payload : {};
    const merged = { ...inner, ...data };
    const bm = merged.identity_manifest || merged.manifest || merged.birth_manifest || {};
    const name = typeof bm.name === 'string' && bm.name.trim() ? bm.name.trim() : 'Kernel';
    const narr = merged.narrative_identity || merged.identity || {};
    let asc = '';
    if (typeof merged.identity_ascription === 'string' && merged.identity_ascription.trim()) {
        asc = merged.identity_ascription.trim();
    } else if (typeof merged.ascription === 'string' && merged.ascription.trim()) {
        asc = merged.ascription.trim();
    } else if (typeof narr.ascription === 'string' && narr.ascription.trim()) {
        asc = narr.ascription.trim();
    } else if (typeof merged.identity_reflection === 'string' && merged.identity_reflection.trim()) {
        asc = merged.identity_reflection.trim().slice(0, 360);
    }
    const parts = [name];
    if (asc) parts.push(asc);
    const digest =
        merged.existence_digest || merged.identity_digest || merged.experience_digest;
    if (typeof digest === 'string' && digest.trim()) {
        parts.push(digest.trim().slice(0, 220));
    }
    if (UI.identityStrip) {
        UI.identityStrip.textContent = parts.join(' — ');
        UI.identityStrip.hidden = false;
    }
    try {
        const care = Number(narr.care_lean);
        const civ = Number(narr.civic_lean);
        if (Number.isFinite(care) && Number.isFinite(civ)) {
            const warmth = Math.max(0, Math.min(1, (care + civ) * 0.5 - 0.35));
            document.documentElement.style.setProperty('--identity-warmth', String(warmth));
        }
    } catch (_) { /* ignore */ }
    try {
        document.title = `Nomad — ${name}`;
    } catch (_) { /* ignore */ }
    applyGestaltPad(merged.gestalt_snapshot || merged.gestalt);
}

/**
 * Append a message to the chat history.
 */
function appendChatMessage(text, roleClass) {
    if(!text) return;
    // Remove placeholder if present
    const placeholder = UI.chatHistory.querySelector('.placeholder');
    if (placeholder) placeholder.remove();
    
    const msgDiv = document.createElement('div');
    msgDiv.className = `chat-msg ${roleClass}`;
    msgDiv.innerText = text;
    UI.chatHistory.appendChild(msgDiv);
    UI.chatHistory.scrollTop = UI.chatHistory.scrollHeight;
    return msgDiv;
}

function _latClass(ttft) {
    if (ttft < 800) return 'fast';
    if (ttft < 2000) return 'mid';
    return 'slow';
}

/**
 * Handle initial Backend Connection
 */
async function connectKernel() {
    console.log("Nomad: Connect button pressed.");
    if (UI.statusText) UI.statusText.innerText = "Connecting...";
    
    if (!window.isSecureContext) {
        console.warn("Nomad: Not running in a Secure Context. Sensors may be blocked.");
        UI.statusText.innerText = "Insecure Context (Sensors Limited)";
    } else {
        UI.statusText.innerText = "Connecting...";
    }
    
    console.log("Nomad: Initializing connection sequence...");

    try {
        teardownKernelSockets();

        let candidates = [];
        try {
            candidates = await resolveKernelEndpointCandidates();
        } catch (e) {
            console.error("Nomad: resolveKernelEndpointCandidates failed:", e);
            alert("Error in candidate resolution: " + e.message);
            throw e;
        }
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

        reconnectAttempts = 0;
        clearKernelReconnectTimer();
        
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
        UI.chatHistory.innerHTML = ""; // Clear
        appendChatMessage("Sys: Nomad Bridge Ready", "kernel");
        
        // Enable the streaming button for Cursor (Block F.2)
        UI.btnStream.disabled = false;
        UI.btnStream.classList.remove('inactive');

        // Enable text input
        UI.chatInput.disabled = false;
        UI.btnSend.disabled = false;

        // Note: wsChat.onopen would be too late here, so we skip it.

        wsChat.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);

                // ── V2 streaming protocol ──────────────────────────────
                if (data.type === 'metadata') {
                    // V2.60: Suppress autonomous metadata entirely
                    if (data.autonomous) return;
                    if (typeof _handleEthicalMetadata === 'function') {
                        _handleEthicalMetadata(data);
                    }
                    if (data.signals && typeof setAppAffectState === 'function') {
                        const risk = data.signals.risk || 0;
                        const urgency = data.signals.urgency || 0;
                        if (risk > 0.5) {
                            setAppAffectState('alarm');
                        } else if (urgency > 0.5) {
                            setAppAffectState('alert');
                        } else {
                            setAppAffectState('calm');
                        }
                    }
                    return;
                }
                if (data.type === 'token') {
                    // V2.60: Skip autonomous tokens — just pulse the dot
                    if (data.autonomous) {
                        const dot = document.getElementById('ethical-heartbeat');
                        if (dot) dot.classList.add('pulsing');
                        return;
                    }
                    let streamDiv = UI.chatHistory.querySelector('.streaming-bubble');
                    if (!streamDiv) {
                        streamDiv = document.createElement('div');
                        streamDiv.className = 'chat-msg kernel streaming-bubble';
                        UI.chatHistory.appendChild(streamDiv);
                    }
                    streamDiv.textContent += data.content;
                    UI.chatHistory.scrollTop = UI.chatHistory.scrollHeight;
                    return;
                }
                if (data.type === 'done') {
                    // V2.60: Autonomous done — stop pulse, no TTS
                    if (data.autonomous) {
                        const dot = document.getElementById('ethical-heartbeat');
                        if (dot) dot.classList.remove('pulsing');
                        return;
                    }
                    const streamDiv = UI.chatHistory.querySelector('.streaming-bubble');
                    const msg = data.message || '';
                    let finalDiv = streamDiv;
                    if (data.blocked) {
                        if (streamDiv) streamDiv.remove();
                        finalDiv = appendChatMessage('\uD83D\uDEAB ' + msg, 'kernel');
                    } else if (streamDiv) {
                        streamDiv.classList.remove('streaming-bubble');
                        if (msg && !streamDiv.textContent.trim()) streamDiv.textContent = msg;
                    } else if (msg) {
                        finalDiv = appendChatMessage(msg, 'kernel');
                    }
                    
                    if (finalDiv && data.latency && data.latency.ttft && !data.blocked) {
                        const badge = document.createElement('span');
                        badge.className = `lat-badge ${_latClass(data.latency.ttft)}`;
                        badge.textContent = `⚡ ${data.latency.ttft.toFixed(0)}ms`;
                        finalDiv.appendChild(badge);
                    }

                    if (msg && UI.transcript) {
                        UI.transcript.innerText = msg;
                        UI.transcript.classList.remove('placeholder');
                    }
                    UI.chatHistory.scrollTop = UI.chatHistory.scrollHeight;
                    return;
                }

                if (data.type === 'tts_audio') {
                    if (data.text) {
                        window.currentEthosText = data.text.toLowerCase().replace(/[^a-záéíóúüñ\s]/g, '');
                    }
                    if (data.audio_b64) {
                        const audio = new Audio("data:audio/mp3;base64," + data.audio_b64);
                        window.currentAudioElement = audio;
                        audio.onplay = () => {
                            window.isEthosSpeaking = true;
                            if (UI.orb) UI.orb.classList.add('speaking');
                        };
                        audio.onended = () => {
                            window.isEthosSpeaking = false;
                            window.currentAudioElement = null;
                            if (UI.orb) UI.orb.classList.remove('speaking');
                        };
                        audio.onerror = () => {
                            window.isEthosSpeaking = false;
                            window.currentAudioElement = null;
                            if (UI.orb) UI.orb.classList.remove('speaking');
                        };
                        audio.play().catch(e => {
                            window.isEthosSpeaking = false;
                            console.warn("TTS play failed:", e);
                        });
                    } else if (data.text) {
                        _speak(data.text);
                    }
                    return;
                }
                // ── end V2 protocol ────────────────────────────────────

                // V2.45: Ethical context HUD
                if (data.type === 'metadata') {
                    _handleEthicalMetadata(data);
                    return;
                }

                // Claude's domain (F.4): detailed message handling
                if (data.role === 'android' || data.final_action) {
                    appendChatMessage(data.content || data.final_action, "kernel");
                }
                
                if (data.type === 'veto') {
                    setAppAffectState('alert');
                    appendChatMessage("KERNEL LOCK: Threat detected.", "kernel");
                }

                if (data.type === 'ping') {
                    console.debug("Nomad: Keep-alive ping from server.");
                }

                if (data.type === 'thought') {
                    if (data.payload && data.payload.dissonance) {
                        UI.chatHistory.parentElement.classList.add('dissonance-active');
                    } else {
                        UI.chatHistory.parentElement.classList.remove('dissonance-active');
                    }
                }
                
                if (data.type === '[SYNC_IDENTITY]' || data.type === 'SYNC_IDENTITY') {
                    applySyncIdentity(data);
                    const inner =
                        data.payload && typeof data.payload === 'object' ? data.payload : {};
                    const narr = data.narrative_identity || inner.narrative_identity || inner.identity || {};
                    const hint =
                        (typeof narr.ascription === 'string' && narr.ascription.trim()) ||
                        (typeof data.identity_ascription === 'string' && data.identity_ascription.trim()) ||
                        (typeof inner.identity_ascription === 'string' && inner.identity_ascription.trim()) ||
                        (typeof inner.identity_reflection === 'string' && inner.identity_reflection.trim().slice(0, 400)) ||
                        'Identity synchronized with kernel.';
                    if (UI.transcript) {
                        UI.transcript.innerText = hint;
                        UI.transcript.classList.remove('placeholder');
                    }
                    flushOutboundChatBuffer();
                    return;
                }

                if (data.event_type === "turn_finished") {
                    const reply = (data.payload && data.payload.response && data.payload.response.message) || "";
                    if (reply && !data.autonomous) {
                        appendChatMessage(reply, "kernel");
                        if (UI.transcript) {
                            UI.transcript.innerText = reply;
                            UI.transcript.classList.remove('placeholder');
                        }
                        _speak(reply);
                    }
                    return;
                }

                if (data.type === 'kernel_voice') {
                    if (data.text) {
                        appendChatMessage(data.text, "kernel");
                        if (UI.transcript) {
                            UI.transcript.innerText = data.text;
                            UI.transcript.classList.remove('placeholder');
                        }
                        _speak(data.text);
                    }
                }

                if (data.type === 'orb_update') {
                    console.log("Nomad: Affective shift", data.archetype);
                    const v = data.visuals;
                    if (v) {
                        UI.orb.style.backgroundColor = v.color;
                        UI.orb.style.boxShadow = `0 0 ${20 * v.scale}px ${10 * v.scale}px ${v.color}`;
                        UI.orb.style.transform = `scale(${v.scale})`;
                        UI.orb.style.animationDuration = `${v.pulse_s}s`;
                    }
                }
            } catch (e) {
                console.warn("Nomad: Chat message parse error", e);
            }
        };

        wsChat.onclose = () => {
            isConnected = false;
            UI.statusDot.classList.remove('connected');
            setAppAffectState('calm');
            UI.btnConnect.disabled = false;
            UI.btnConnect.innerText = 'Reconnect';
            UI.btnStream.disabled = true;
            UI.btnStream.classList.add('inactive');
            UI.chatInput.disabled = true;
            UI.btnSend.disabled = true;
            scheduleKernelReconnect('chat');
        };

        wsNomad.onclose = () => {
            isConnected = false;
            UI.statusDot.classList.remove('connected');
            setAppAffectState('calm');
            UI.btnConnect.disabled = false;
            UI.btnConnect.innerText = 'Reconnect';
            UI.btnStream.disabled = true;
            UI.btnStream.classList.add('inactive');
            scheduleKernelReconnect('nomad');
        };

        function armNomadPingHeartbeat() {
            console.log('Nomad Sensory Bridge sideband armed');
            if (nomadPingIntervalId != null) {
                try { clearInterval(nomadPingIntervalId); } catch (e) { /* ignore */ }
                nomadPingIntervalId = null;
            }
            if (nomadHeartbeatIntervalId != null) {
                try { clearInterval(nomadHeartbeatIntervalId); } catch (e) { /* ignore */ }
                nomadHeartbeatIntervalId = null;
            }
            nomadHeartbeatIntervalId = setInterval(() => {
                try {
                    if (wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                        wsNomad.send(JSON.stringify({ type: 'telemetry', payload: { heartbeat: true } }));
                    }
                } catch (e) {
                    console.warn('Nomad heartbeat send failed', e);
                }
            }, 15000);
            nomadPingIntervalId = setInterval(() => {
                try {
                    if (wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                        nomadBridgePingT0 = performance.now();
                        wsNomad.send(JSON.stringify({ type: 'ping', payload: {} }));
                    }
                } catch (e) {
                    console.warn('Nomad bridge ping failed', e);
                }
            }, 10000);
        }
        wsNomad.onopen = armNomadPingHeartbeat;
        if (wsNomad.readyState === WebSocket.OPEN) {
            armNomadPingHeartbeat();
        }

        wsNomad.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                if (msg.type === 'SYNC_IDENTITY' || msg.type === '[SYNC_IDENTITY]') {
                    applySyncIdentity(msg);
                    const inner =
                        msg.payload && typeof msg.payload === 'object' ? msg.payload : {};
                    const narr = msg.narrative_identity || inner.narrative_identity || inner.identity || {};
                    const hint =
                        (typeof narr.ascription === 'string' && narr.ascription.trim()) ||
                        (typeof msg.identity_ascription === 'string' && msg.identity_ascription.trim()) ||
                        (typeof inner.identity_ascription === 'string' && inner.identity_ascription.trim()) ||
                        (typeof inner.identity_reflection === 'string' && inner.identity_reflection.trim().slice(0, 400)) ||
                        'Identity synchronized (Nomad bridge).';
                    if (UI.transcript) {
                        UI.transcript.innerText = hint;
                        UI.transcript.classList.remove('placeholder');
                    }
                    flushOutboundChatBuffer();
                    return;
                }
                if (msg.type === 'pong' && msg.payload && nomadBridgePingT0 != null) {
                    const rttMs = Math.round(performance.now() - nomadBridgePingT0);
                    nomadBridgePingT0 = null;
                    console.debug('Nomad bridge RTT (ms):', rttMs);
                    if (UI.nomadRtt) {
                        UI.nomadRtt.textContent = `${rttMs} ms`;
                    }
                    return;
                }
                if (msg.type === 'charm_feedback') {
                    console.debug('Nomad charm_feedback', msg.payload);
                    const payload = msg.payload || {};
                    if (payload.type === 'kernel_voice' || payload.text || payload.content) {
                        const text = payload.text || payload.content || '';
                        if (text) {
                            appendChatMessage(text, "kernel");
                            if (UI.transcript) {
                                UI.transcript.innerText = `[Proxied] Kernel: ${text}`;
                            }
                            if ('speechSynthesis' in window) {
                                const utterance = new SpeechSynthesisUtterance(text);
                                utterance.lang = 'es-ES';
                                const voices = window.speechSynthesis.getVoices();
                                const preferred = voices.find(v => v.lang.startsWith("es")) || voices[0];
                                if (preferred) utterance.voice = preferred;
                                window.speechSynthesis.speak(utterance);
                            }
                        }
                    }
                    if (payload.type === 'haptic_feedback' || payload.haptics) {
                        const pattern = payload.haptics || [200, 100, 200];
                        if (navigator.vibrate) navigator.vibrate(pattern);
                    }
                }

                // ── Server-pushed telemetry updates (HUD spans) ──────────────
                if (msg.type === 'telemetry' && msg.payload) {
                    const p = msg.payload;
                    if (p.battery !== undefined && UI.telBat) {
                        UI.telBat.textContent = Math.round(p.battery * 100) + '%';
                    }
                    if (p.temp !== undefined && UI.telTemp) {
                        UI.telTemp.textContent = Number(p.temp).toFixed(1) + '°';
                    }
                    if (p.kinetics !== undefined && UI.telKin) {
                        UI.telKin.textContent = Number(p.kinetics).toFixed(1);
                    }
                    if (p.cpu_usage !== undefined) {
                        const cpuEl = document.getElementById('tel-cpu');
                        if (cpuEl) cpuEl.textContent = Number(p.cpu_usage).toFixed(0) + '%';
                    }
                    if (p.ram_usage !== undefined) {
                        const ramEl = document.getElementById('tel-ram');
                        if (ramEl) ramEl.textContent = Number(p.ram_usage).toFixed(0) + '%';
                    }
                    if (p.rtt_ms !== undefined && UI.nomadRtt) {
                        UI.nomadRtt.textContent = Math.round(p.rtt_ms) + ' ms';
                    }
                }
                // ── V2.13 Fix: forward vision signals to /ws/chat ────────────
                // wsNomad receives vision_signals; wsChat needs them for context injection.
                if (msg.type === 'vision_signals' && msg.payload) {
                    // Update local HUD telemetry (audio channel proxy)
                    if (UI.telAud && msg.payload.brightness !== undefined) {
                        UI.telAud.textContent = Number(msg.payload.brightness).toFixed(2);
                    }
                    // Forward to wsChat so text turns get physical context too
                    if (wsChat && wsChat.readyState === WebSocket.OPEN) {
                        try {
                            wsChat.send(JSON.stringify({
                                type: 'vision_context',
                                payload: msg.payload,
                            }));
                        } catch (_) { /* non-fatal */ }
                    }
                    return;
                }
            } catch (e) {
                console.warn('Nomad WS message parse error', e);
            }
        };

        flushOutboundChatBuffer();
    } catch (err) {
        console.error("Nomad Bridge connection fatal:", err);
        alert("Connection Error: " + err.message);
        scheduleKernelReconnect('fatal');
    }
}


window.addEventListener('DOMContentLoaded', () => {


    function initNomadUiModeFromQuery() {
        const params = new URLSearchParams(window.location.search);
        if (params.get('ui') === 'full') {
            document.body.classList.remove('nomad-text-focus');
        }
    }

    function syncUiModeButtonLabel() {
        if (UI.btnUiMode) {
            if (document.body.classList.contains('nomad-text-focus')) {
                UI.btnUiMode.innerText = "Full UI";
            } else {
                UI.btnUiMode.innerText = "Text Mode";
            }
        }
    }

    try {
        initNomadUiModeFromQuery();
        syncUiModeButtonLabel();
    } catch (e) {
        console.warn("Nomad UI init error", e);
    }

    if (UI.btnUiMode) {
        UI.btnUiMode.addEventListener('click', () => {
            document.body.classList.toggle('nomad-text-focus');
            syncUiModeButtonLabel();
        });
    }

    if (UI.btnInstall) {
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
    }

    if (UI.btnConnect) UI.btnConnect.addEventListener('click', connectKernel);
    
    let isStreaming = false;
    if (UI.btnStream)  UI.btnStream.addEventListener('click', () => {
        if (!isStreaming) {
            if (typeof startSensors === 'function') startSensors();
            isStreaming = true;
            UI.btnStream.innerText = "SENSORS ON";
            UI.btnStream.style.backgroundColor = "#1f6feb";
            if (UI.statusDot) UI.statusDot.style.boxShadow = "0 0 12px #1f6feb";
        } else {
            if (typeof stopSensors === 'function') stopSensors();
            isStreaming = false;
            UI.btnStream.innerText = "STREAM";
            UI.btnStream.style.backgroundColor = "";
            if (UI.statusDot) UI.statusDot.style.boxShadow = "";
            UI.transcript.innerText = "Sensors Off.";
            UI.transcript.classList.add('placeholder');
        }
    });

    if (UI.btnSend)    UI.btnSend.addEventListener('click', sendNomadChatMessage);
    if (UI.chatInput)  UI.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendNomadChatMessage();
    });

    if ('getBattery' in navigator) {
        navigator.getBattery().then(bat => {
            const up = () => updateHud('bat', bat.level);
            bat.addEventListener('levelchange', up);
            up();
        });
    }

    // Service Worker disabled for LAN/Insecure context testing (avoids HTTPS upgrade loops)
    /*
    if ('serviceWorker' in navigator) {
        navigator.serviceWorker.register('./sw.js?v=22.0.2')
            .then(reg => console.log('Nomad Service Worker registered', reg))
            .catch(err => console.error('SW block:', err));
    }
    */

    console.log("Nomad PWA V13.1.9 Initialized (SW Disabled).");
});

