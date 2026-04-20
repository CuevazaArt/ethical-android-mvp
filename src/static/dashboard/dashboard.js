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
};

const state = {
    kinetics: 0,
    heartbeat: false,
    dissonance: false,
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
    if (payload.tension !== undefined) {
        EL.tension.textContent = asFloat(payload.tension).toFixed(3);
    }
    if (payload.trust !== undefined) {
        EL.trust.textContent = asFloat(payload.trust).toFixed(3);
    }
    if (payload.battery !== undefined) {
        EL.battery.textContent = asFloat(payload.battery).toFixed(3);
    }
    if (payload.temp !== undefined) {
        EL.temp.textContent = asFloat(payload.temp).toFixed(3);
    }
    if (payload.kinetics !== undefined) {
        state.kinetics = asFloat(payload.kinetics);
        EL.kinetics.textContent = state.kinetics.toFixed(3);
    }
    if (payload.heartbeat !== undefined) {
        state.heartbeat = !!payload.heartbeat;
        setBool(EL.heartbeat, state.heartbeat);
    }
}

function updateAudio(rms) {
    EL.audioRms.textContent = asFloat(rms).toFixed(3);
}

function updateVision(b64) {
    if (!b64) return;
    const ctx = EL.canvas.getContext('2d');
    const img = new Image();
    img.onload = () => {
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
    EL.thought.textContent = text || '';
    state.dissonance = !!dissonance;
    setBool(EL.dissonance, state.dissonance);
    appendLog(`kernel: ${text || ''}`, dissonance ? 'warn' : 'info');
}

function handleMessage(msg) {
    if (!msg || typeof msg !== 'object') return;

    switch (msg.type) {
        case 'telemetry':
            updateTelemetry(msg.payload);
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
        default:
            appendLog(`event: ${JSON.stringify(msg)}`, 'debug');
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
