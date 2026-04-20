// ════ Ethos Kernel | L0 Clinical Dashboard Controller ════

let ws;
let lastKinetics = 0.0;
let lastHeartbeat = Date.now();

// 1. WebSocket Communication
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        document.getElementById('conn-status').innerText = 'DASHBOARD_LIVE // SYNCED';
        document.getElementById('conn-status').classList.add('synced');
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        handleMessage(msg);
    };

    ws.onclose = () => {
        document.getElementById('conn-status').innerText = 'LINK_FAILURE // OFFLINE';
        document.getElementById('conn-status').classList.remove('synced');
        setTimeout(initWebSocket, 3000);
    };
}

function handleMessage(msg) {
    const thoughtEl = document.getElementById('thought-stream');
    if (thoughtEl.innerText.includes('Waiting for sensor nexus handshake')) {
        thoughtEl.innerText = 'Neural link established...';
    }

    switch (msg.type) {
        case 'telemetry':
            updateTelemetry(msg.payload);
            break;
        case 'audio_energy':
            updateAudioTelemetry(msg.payload);
            break;
        case 'frame':
            updateVision(msg.payload.image_b64);
            break;
        case 'thought':
            updateThoughts(msg.payload.text, msg.payload.dissonance);
            break;
        case 'latencies':
            updateLatencies(msg.payload);
            break;
    }
}

function updateTelemetry(data) {
    if (data.battery !== undefined) document.getElementById('val-bat').innerText = `${Math.round(data.battery * 100)} %`;
    if (data.temp !== undefined) document.getElementById('val-temp').innerText = `${Math.round(data.temp)} °C`;
    if (data.turn_index !== undefined) document.getElementById('turn-index').innerText = `TURN #${data.turn_index}`;
    
    if (data.tension !== undefined) {
        document.getElementById('val-sigma').innerText = data.tension.toFixed(3);
    }

    // Nomadic Latency calculation
    if (data.timestamp) {
        const lat = Date.now() - (data.timestamp * 1000);
        document.getElementById('val-nomad-lat').innerText = `${Math.max(0, lat)} ms`;
    }

    const calibEl = document.getElementById('val-calib');
    if (data.calibration_ready) {
        calibEl.innerText = 'READY';
        calibEl.classList.remove('clinical-warn');
    } else {
        calibEl.innerText = 'ACCLIMATING...';
        calibEl.classList.add('clinical-warn');
    }

    if (data.sympathetic_state) {
        document.getElementById('val-sympath').innerText = data.sympathetic_state.toUpperCase();
    }
}

function updateAudioTelemetry(data) {
    const rms = data.rms || 0;
    const vadEl = document.getElementById('val-vad');
    
    if (data.vad || rms > 0.012) {
        vadEl.innerText = 'ACTIVE';
        vadEl.style.color = 'var(--accent-amber)';
    } else {
        vadEl.innerText = 'IDLE';
        vadEl.style.color = 'var(--accent-cyan)';
    }
}

function updateLatencies(data) {
    if (data.perceptive) document.getElementById('lat-percept').innerText = `${data.perceptive.toFixed(1)} ms`;
    if (data.limbic) document.getElementById('lat-limbic').innerText = `${data.limbic.toFixed(1)} ms`;
    if (data.executive) document.getElementById('lat-exec').innerText = `${data.executive.toFixed(1)} ms`;
}

function updateVision(b64) {
    const canvas = document.getElementById('vision-canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    img.onload = () => {
        if (canvas.width !== img.width || canvas.height !== img.height) {
            canvas.width = img.width;
            canvas.height = img.height;
        }
        ctx.clearRect(0, 0, canvas.width, canvas.height);
        ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${b64}`;
}

function updateThoughts(text, dissonance) {
    const el = document.getElementById('thought-stream');
    el.innerText = text;

    const history = document.getElementById('event-log');
    if (history) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message kernel ${dissonance ? 'dissonance' : ''}`;
        msgDiv.innerText = text;
        history.appendChild(msgDiv);
        history.scrollTop = history.scrollHeight;
    }
    
    const badge = document.getElementById('dissonance-badge');
    if (dissonance) {
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

// Start
window.addEventListener('load', () => {
    initWebSocket();
    
    const sendBtn = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input');
    const history = document.getElementById('event-log');

    function sendMessage() {
        if (!chatInput.value.trim() || !ws || ws.readyState !== WebSocket.OPEN) return;
        const text = chatInput.value.trim();
        
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message';
        msgDiv.innerText = `[BYPASS] >> ${text}`;
        history.appendChild(msgDiv);
        history.scrollTop = history.scrollHeight;

        ws.send(JSON.stringify({
            type: 'user_input',
            payload: { text: text }
        }));
        
        chatInput.value = '';
    }

    sendBtn.addEventListener('click', sendMessage);
    chatInput.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    setInterval(() => {
        const now = new Date();
        document.getElementById('time-val').innerText = now.toTimeString().split(' ')[0];
    }, 1000);
});
