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
    identityStrip: document.getElementById('identity-strip'),
    btnUiMode: document.getElementById('btn-ui-mode'),
    btnInstall: document.getElementById('btn-install'),
    chatInput: document.getElementById('chat-input'),
    btnSend: document.getElementById('btn-send'),
    telBat: document.getElementById('tel-bat'),
    telTemp: document.getElementById('tel-temp'),
    telKin: document.getElementById('tel-kin'),
    telAud: document.getElementById('tel-aud'),
    nomadRtt: document.getElementById('nomad-rtt'),
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

    if (trySendChatWsJSON({ text })) {
        nomadApplySendingUi(true);
        return;
    }
    if (trySendNomadChatRelay(text)) {
        nomadApplySendingUi(true);
        return;
    }
    enqueueOutboundChat(text);
    nomadApplySendingUi(false);
    if (UI.statusText) UI.statusText.innerText = 'Queued (waiting for link)…';
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
    const textFocus = document.body.classList.contains('nomad-text-focus');
    document.body.className = '';
    if (textFocus) {
        document.body.classList.add('nomad-text-focus');
    }
    if (state && state !== 'calm') {
        document.body.classList.add(`state-${state}`);
    }
}

/** Bloque 22.3 — PAD / sigma from gestalt dict (server ``sync_identity_v2``). */
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
        teardownKernelSockets();

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
        
        // Enable the streaming button for Cursor (Block F.2)
        UI.btnStream.disabled = false;
        UI.btnStream.classList.remove('inactive');

        // Note: wsChat.onopen would be too late here, so we skip it.

        wsChat.onmessage = (event) => {
            try {
                const data = JSON.parse(event.data);
                if (data.type === '[SYNC_IDENTITY]' || data.type === 'SYNC_IDENTITY') {
                    const inner =
                        data.payload && typeof data.payload === 'object' ? data.payload : {};
                    applySyncIdentity({
                        ...inner,
                        narrative_identity: data.narrative_identity || inner.narrative_identity,
                        identity: data.identity || inner.identity,
                        manifest: data.manifest || inner.identity_manifest,
                        identity_manifest: inner.identity_manifest || data.manifest,
                        gestalt_snapshot: inner.gestalt_snapshot || data.gestalt_snapshot || data.gestalt,
                        identity_ascription: inner.identity_ascription || data.identity_ascription,
                        identity_reflection: inner.identity_reflection || data.identity_reflection,
                        existence_digest: inner.existence_digest || data.existence_digest,
                        experience_digest: inner.experience_digest || data.experience_digest,
                    });
                    const narr = data.narrative_identity || inner.narrative_identity || inner.identity || {};
                    const hint =
                        (typeof narr.ascription === 'string' && narr.ascription.trim()) ||
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
                    const msg = data.payload?.response?.message || "";
                    if (msg && UI.transcript) {
                        UI.transcript.innerText = msg;
                        UI.transcript.classList.remove('placeholder');
                    }
                    return;
                }
                if (data.type === 'kernel_voice' && data.text && UI.transcript) {
                    UI.transcript.innerText = data.text;
                    UI.transcript.classList.remove('placeholder');
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
                    const inner =
                        msg.payload && typeof msg.payload === 'object' ? msg.payload : {};
                    applySyncIdentity({
                        ...inner,
                        narrative_identity: msg.narrative_identity || inner.narrative_identity,
                        identity: msg.identity || inner.identity,
                        manifest: msg.manifest || inner.identity_manifest,
                        identity_manifest: inner.identity_manifest || msg.manifest,
                        gestalt_snapshot: inner.gestalt_snapshot || msg.gestalt_snapshot || msg.gestalt,
                        identity_ascription: inner.identity_ascription || msg.identity_ascription,
                        identity_reflection: inner.identity_reflection || msg.identity_reflection,
                        existence_digest: inner.existence_digest || msg.existence_digest,
                        experience_digest: inner.experience_digest || msg.experience_digest,
                    });
                    const narr = msg.narrative_identity || inner.narrative_identity || inner.identity || {};
                    const hint =
                        (typeof narr.ascription === 'string' && narr.ascription.trim()) ||
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
                        if (text && UI.transcript) {
                            UI.transcript.innerText = `[Proxied] Kernel: ${text}`;
                            if ('speechSynthesis' in window) {
                                const utterance = new SpeechSynthesisUtterance(text);
                                window.speechSynthesis.speak(utterance);
                            }
                        }
                    }
                    if (payload.type === 'haptic_feedback' || payload.haptics) {
                        const pattern = payload.haptics || [200, 100, 200];
                        if (navigator.vibrate) navigator.vibrate(pattern);
                    }
                }
            } catch (e) {
                console.warn('Nomad WS message parse error', e);
            }
        };

        flushOutboundChatBuffer();

    } catch (e) {
        alert(`Connectivity Error: ${e.message || e}\n\nTroubleshoot:\n1. Ensure you are on the SAME Wi-Fi.\n2. Allow port 8765 in Windows Firewall (PC).\n3. Keep mobile browser 'Shields' off for this IP.`);
        UI.statusText.innerText = "Error";
    }
}

function initNomadUiModeFromQuery() {
    try {
        const q = new URLSearchParams(window.location.search);
        if (q.get('fullui') === '1' || q.get('text') === '0' || q.get('solo_text') === '0') {
            document.body.classList.remove('nomad-text-focus');
        }
        if (q.get('mode') === 'text' || q.get('solo') === '1' || q.get('text') === '1' || q.get('solo_text') === '1') {
            document.body.classList.add('nomad-text-focus');
        }
    } catch (_) { /* ignore */ }
}

function syncUiModeButtonLabel() {
    if (!UI.btnUiMode) return;
    UI.btnUiMode.textContent = document.body.classList.contains('nomad-text-focus')
        ? 'Full UI'
        : 'Text focus';
}

initNomadUiModeFromQuery();
syncUiModeButtonLabel();

if (UI.btnUiMode) {
    UI.btnUiMode.addEventListener('click', () => {
        document.body.classList.toggle('nomad-text-focus');
        syncUiModeButtonLabel();
    });
}

// Application Installation (PWA Service Worker)
let deferredPrompt;
window.addEventListener('beforeinstallprompt', (e) => {
    e.preventDefault();
    deferredPrompt = e;
});

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

// ── Sensory HUD Updates ──────────────────────────────────────────────────
function updateHud(type, val) {
    try {
        const n = Number(val);
        const ok = Number.isFinite(n);
        if (type === 'bat' && UI.telBat) {
            UI.telBat.innerText = ok ? `${Math.round(n * 100)}%` : '--';
        }
        if (type === 'temp' && UI.telTemp) {
            UI.telTemp.innerText = ok ? `${Math.round(n)}°` : '--';
        }
        if (type === 'kin' && UI.telKin) {
            UI.telKin.innerText = ok ? n.toFixed(1) : '0.0';
        }
        if (type === 'aud' && UI.telAud) {
            UI.telAud.innerText = ok ? n.toFixed(2) : '0.00';
        }
    } catch (_) { /* ignore */ }
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
        navigator.serviceWorker.register('./sw.js?v=13.1.7')
            .then(reg => console.log('Nomad Service Worker registered', reg))
            .catch(err => console.error('SW block:', err));
    });
}

console.log("Nomad PWA V13.1.7 Initialized.");
