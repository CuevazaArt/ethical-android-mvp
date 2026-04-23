// Ethos Kernel Clinical Dashboard Controller (Bloque 14.2)

let ws = null;

const EL = {
    connStatus: document.getElementById('conn-status'),
    turnIndex: document.getElementById('turn-index'),
    timeVal: document.getElementById('time-val'),
    tension: document.getElementById('tension-val'),
    trust: document.getElementById('trust-val'),
    audioRms: document.getElementById('audio-rms-val'),
    battery: document.getElementById('bat-val'),
    temp: document.getElementById('temp-val'),
    kinetics: document.getElementById('kin-val'),
    connected: document.getElementById('flag-connected'),
    dissonance: document.getElementById('flag-dissonance'),
    heartbeat: document.getElementById('flag-heartbeat'),
    thought: document.getElementById('thought-stream'),
    log: document.getElementById('event-log'),
    sendBtn: document.getElementById('chat-send'),
    chatInput: document.getElementById('chat-input'),
    canvas: document.getElementById('vision-canvas'),
    chatHistory: document.getElementById('chat-history'),
    orbPreview: document.getElementById('orb-preview'),
    vesselId: document.getElementById('vessel-id'),
    syncStatus: document.getElementById('sync-status'),
    rtt: document.getElementById('rtt-val'),
    vitality: document.getElementById('vitality-val'),
    orient: document.getElementById('orient-val'),
    socialCircle: document.getElementById('social-circle'),
    socialPosture: document.getElementById('social-posture'),
    bayesConf: document.getElementById('bayes-conf'),
    bayesDelta: document.getElementById('bayes-delta'),
    llmMode: document.getElementById('llm-mode'),
    llmModel: document.getElementById('llm-model'),
    llmStatus: document.getElementById('llm-status'),
    vadState: document.getElementById('vad-state'),
    cpuUsage: document.getElementById('cpu-usage'),
    ramUsage: document.getElementById('ram-usage'),
    govStatus: document.getElementById('gov-status'),
    identityEpoch: document.getElementById('identity-epoch'),
    episodeCount: document.getElementById('episode-count'),
    identityDigest: document.getElementById('identity-digest'),
    padState: document.getElementById('pad-state'),
    affectArchetype: document.getElementById('affect-archetype'),
};

const state = {
    kinetics: 0,
    heartbeat: false,
    dissonance: false,
    orbColor: '#38bdf8',
    lastVesselUpdate: 0,
};

function asFloat(v, fallback = 0) {
    const n = Number(v);
    return Number.isFinite(n) ? n : fallback;
}

function setBool(el, value) {
    el.textContent = value ? 'true' : 'false';
    el.classList.toggle('bool-true', !!value);
    el.classList.toggle('bool-false', !value);
}

function appendLog(line, level = 'info') {
    const row = document.createElement('div');
    row.className = `log-row ${level}`;
    row.textContent = line;
    EL.log.appendChild(row);
    EL.log.scrollTop = EL.log.scrollHeight;

    const maxRows = 200;
    while (EL.log.children.length > maxRows) {
        EL.log.removeChild(EL.log.firstChild);
    }
}

function updateClock() {
    const now = new Date();
    EL.timeVal.textContent = now.toTimeString().split(' ')[0];
}

function updateTelemetry(payload) {
    if (!payload || typeof payload !== 'object') return;

    if (payload.turn_index !== undefined) {
        EL.turnIndex.textContent = `TURN #${payload.turn_index}`;
    }
    if (payload.tension !== undefined) EL.tension.textContent = asFloat(payload.tension).toFixed(3);
    if (payload.trust !== undefined) EL.trust.textContent = asFloat(payload.trust).toFixed(3);
    if (payload.battery !== undefined) EL.battery.textContent = payload.battery;
    if (payload.temp !== undefined) EL.temp.textContent = payload.temp;
    if (payload.kinetics !== undefined) {
        state.kinetics = asFloat(payload.kinetics);
        EL.kinetics.textContent = state.kinetics.toFixed(3);
    }
    if (payload.heartbeat !== undefined) {
        state.heartbeat = !!payload.heartbeat;
        setBool(EL.heartbeat, state.heartbeat);
    }
    
    // New 12-domain specific fields
    if (payload.vitality !== undefined) EL.vitality.textContent = asFloat(payload.vitality).toFixed(2);
    if (payload.orientation) EL.orient.textContent = JSON.stringify(payload.orientation);
    if (payload.social_circle) EL.socialCircle.textContent = payload.social_circle;
    if (payload.social_posture) EL.socialPosture.textContent = payload.social_posture;
    if (payload.bayes_confidence !== undefined) EL.bayesConf.textContent = asFloat(payload.bayes_confidence).toFixed(3);
    if (payload.bayes_delta !== undefined) EL.bayesDelta.textContent = asFloat(payload.bayes_delta).toFixed(3);
    
    if (payload.llm_mode !== undefined) EL.llmMode.textContent = payload.llm_mode;
    if (payload.llm_model !== undefined && EL.llmModel) EL.llmModel.textContent = payload.llm_model;
    if (payload.llm_status !== undefined && EL.llmStatus) {
        EL.llmStatus.textContent = payload.llm_status;
        EL.llmStatus.style.color = payload.llm_status === 'active' ? 'var(--ok)' : 'var(--warn)';
    }
    if (payload.vad_state !== undefined) EL.vadState.textContent = payload.vad_state;
    if (payload.cpu_usage !== undefined) EL.cpuUsage.textContent = asFloat(payload.cpu_usage).toFixed(1) + "%";
    if (payload.ram_usage !== undefined) EL.ramUsage.textContent = asFloat(payload.ram_usage).toFixed(1) + "%";
    if (payload.gov_status !== undefined) EL.govStatus.textContent = payload.gov_status;

    // Vessel latency
    if (payload.vessel_id) EL.vesselId.textContent = payload.vessel_id;
    EL.syncStatus.textContent = "active";
    const now = Date.now();
    if (state.lastVesselUpdate > 0) {
        EL.rtt.textContent = (now - state.lastVesselUpdate) + " ms";
    }
    state.lastVesselUpdate = now;
    
    // Identity & Memory
    if (payload.identity_epoch !== undefined && EL.identityEpoch) EL.identityEpoch.textContent = payload.identity_epoch;
    if (payload.episode_count !== undefined && EL.episodeCount) EL.episodeCount.textContent = payload.episode_count;
    if (payload.identity_digest && EL.identityDigest) EL.identityDigest.textContent = payload.identity_digest;
    
    // Limbic Affect Orb — color shifts from blue (calm) to red (danger)
    if (payload.tension !== undefined && EL.orbPreview) {
        const t = Math.min(1, Math.max(0, asFloat(payload.tension)));
        // Hue: 200 (blue/calm) → 0 (red/danger)
        const hue = Math.round(200 * (1 - t));
        const sat = 70 + Math.round(t * 30);
        const color = `hsl(${hue}, ${sat}%, 55%)`;
        EL.orbPreview.style.background = color;
        EL.orbPreview.style.boxShadow = `0 0 ${15 + t * 25}px ${color}`;
        state.orbColor = color;
    }
    if (payload.pad_state && EL.padState) EL.padState.textContent = payload.pad_state;
    if (payload.dominant_archetype && EL.affectArchetype) EL.affectArchetype.textContent = payload.dominant_archetype;
}

function updateAudio(rms) {
    const val = asFloat(rms);
    EL.audioRms.textContent = val.toFixed(3);
    // Visual feedback on the Orb Preview
    if (EL.orbPreview) {
        const scale = 1 + (val * 0.5);
        EL.orbPreview.style.transform = `scale(${scale})`;
        EL.orbPreview.style.boxShadow = `0 0 ${15 + (val * 20)}px ${state.orbColor}`;
    }
}

function updateVision(b64) {
    if (!b64) return;
    const ctx = EL.canvas.getContext('2d');
    const img = new Image();
    img.onload = () => {
        // Force non-scroll by fitting to parent
        const parentW = EL.canvas.parentElement.clientWidth - 16;
        const parentH = EL.canvas.parentElement.clientHeight - 40;
        
        if (EL.canvas.width !== img.width || EL.canvas.height !== img.height) {
            EL.canvas.width = img.width;
            EL.canvas.height = img.height;
        }
        ctx.clearRect(0, 0, EL.canvas.width, EL.canvas.height);
        ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${b64}`;
}

function updateThought(text, dissonance) {
    if (!text) return;
    EL.thought.textContent = text;
    state.dissonance = !!dissonance;
    setBool(EL.dissonance, state.dissonance);
    
    // Add to chat history too if it's a kernel response
    const row = document.createElement('div');
    row.className = `log-row ${dissonance ? 'warn' : 'ok'}`;
    row.textContent = `KERNEL> ${text}`;
    EL.chatHistory.appendChild(row);
    EL.chatHistory.scrollTop = EL.chatHistory.scrollHeight;
    
    appendLog(`kernel: ${text}`, dissonance ? 'warn' : 'info');
}

function updateThoughtStream(chunk) {
    if (!chunk) return;
    EL.thought.textContent += chunk;
}


function handleMessage(msg) {
    if (!msg || typeof msg !== 'object') return;

    switch (msg.type) {
        case 'telemetry':
            updateTelemetry(msg.payload);
            break;
        case 'telemetry_update': // Bloque 24.0: Integración Dashboard LTM
            if (msg.payload && msg.payload.ltm_rescue) {
                appendLog(`[LTM RETRIEVAL] ${msg.payload.ltm_rescue}`, 'info');
            }
            break;
        case 'audio_energy':
            updateAudio(msg.payload?.rms);
            break;
        case 'frame':
            updateVision(msg.payload?.image_b64);
            break;
        case 'thought':
            updateThought(msg.payload?.text, msg.payload?.dissonance);
            break;
        case 'thought_stream':
            updateThoughtStream(msg.payload?.chunk);
            break;
        case 'thought_flush':
            EL.thought.textContent = "[Pensando... ] "; // Clear before next thought stream and show indicator
            break;
        case 'turn_finished':
            // Final response from kernel
            if (msg.payload?.response?.message) {
                updateThought(msg.payload.response.message, false);
            }
            break;
        default:
            appendLog(`event: ${msg.type}`, 'debug');
            break;
    }
}

function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;

    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        EL.connStatus.textContent = 'ONLINE';
        setBool(EL.connected, true);
        appendLog('dashboard websocket connected', 'ok');
    };

    ws.onmessage = (event) => {
        try {
            handleMessage(JSON.parse(event.data));
        } catch (e) {
            appendLog(`parse_error: ${String(e)}`, 'error');
        }
    };

    ws.onclose = () => {
        EL.connStatus.textContent = 'RECONNECTING';
        setBool(EL.connected, false);
        appendLog('dashboard websocket disconnected', 'warn');
        setTimeout(initWebSocket, 2500);
    };

    ws.onerror = () => {
        appendLog('dashboard websocket error', 'error');
    };
}

function sendOperatorMessage() {
    const text = (EL.chatInput.value || '').trim();
    if (!text || !ws || ws.readyState !== WebSocket.OPEN) {
        return;
    }
    ws.send(JSON.stringify({ type: 'user_input', payload: { text } }));
    
    // Add to chat history
    const row = document.createElement('div');
    row.className = `log-row operator`;
    row.textContent = `OPERATOR> ${text}`;
    EL.chatHistory.appendChild(row);
    EL.chatHistory.scrollTop = EL.chatHistory.scrollHeight;

    appendLog(`operator: ${text}`, 'operator');
    EL.chatInput.value = '';
}

window.addEventListener('load', () => {
    setBool(EL.connected, false);
    setBool(EL.dissonance, false);
    setBool(EL.heartbeat, false);

    initWebSocket();
    updateClock();
    setInterval(updateClock, 1000);

    EL.sendBtn.addEventListener('click', sendOperatorMessage);
    EL.chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendOperatorMessage();
    });
});
