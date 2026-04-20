// ════ Ethos Kernel | L0 Dashboard Controller ════

let scene, camera, renderer, globe;
let ws;
let visualTension = 0.0;
let lastKinetics = 0.0;
const orbContainer = document.getElementById('orb-container');

// 1. Initialize 3D Orb (Affective Visualization)
function initOrb() {
    scene = new THREE.Scene();
    camera = new THREE.PerspectiveCamera(75, orbContainer.offsetWidth / orbContainer.offsetHeight, 0.1, 1000);
    
    renderer = new THREE.WebGLRenderer({ alpha: true, antialias: true });
    renderer.setSize(orbContainer.offsetWidth, orbContainer.offsetHeight);
    orbContainer.appendChild(renderer.domElement);

    const geometry = new THREE.SphereGeometry(2, 64, 64);
    const material = new THREE.MeshPhongMaterial({
        color: 0x4f46e5,
        wireframe: true,
        transparent: true,
        opacity: 0.8,
        emissive: 0x06b6d4,
        emissiveIntensity: 0.5
    });

    globe = new THREE.Mesh(geometry, material);
    scene.add(globe);

    const light = new THREE.PointLight(0xffffff, 1, 100);
    light.position.set(10, 10, 10);
    scene.add(light);

    const ambientLight = new THREE.AmbientLight(0x404040);
    scene.add(ambientLight);

    camera.position.z = 5;

    animate();
}

function animate() {
    requestAnimationFrame(animate);
    globe.rotation.y += 0.005;
    globe.rotation.x += 0.002;
    renderer.render(scene, camera);
}

// 2. WebSocket Communication
function initWebSocket() {
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    const wsUrl = `${protocol}//${window.location.host}/ws/dashboard`;
    
    ws = new WebSocket(wsUrl);

    ws.onopen = () => {
        document.getElementById('conn-status').innerText = 'DASHBOARD SYNCED';
        document.getElementById('conn-status').classList.add('synced');
    };

    ws.onmessage = (event) => {
        const msg = JSON.parse(event.data);
        handleMessage(msg);
    };

    ws.onclose = () => {
        document.getElementById('conn-status').innerText = 'CONNECTION LOST';
        setTimeout(initWebSocket, 3000);
    };
}

function handleMessage(msg) {
    // Clear initial handshake message on first real data
    const thoughtEl = document.getElementById('thought-stream');
    if (thoughtEl.innerText.includes('Waiting for sensor nexus handshake')) {
        thoughtEl.innerText = 'Neural link established...';
    }

    switch (msg.type) {
        case 'telemetry':
            updateTelemetry(msg.payload);
            break;
        case 'audio_energy':
            updateAudio(msg.payload.rms);
            break;
        case 'frame':
            updateVision(msg.payload.image_b64);
            break;
        case 'thought':
            updateThoughts(msg.payload.text, msg.payload.dissonance);
            break;
    }
}

function updateTelemetry(data) {
    if (data.battery) document.getElementById('bat-val').innerText = `${Math.round(data.battery)}%`;
    if (data.temp) document.getElementById('temp-val').innerText = `${Math.round(data.temp)}°C`;
    if (data.turn_index) document.getElementById('turn-index').innerText = `TURN #${data.turn_index}`;
    if (data.trust) {
        document.getElementById('trust-val').innerText = data.trust.toFixed(2);
        document.getElementById('trust-fill').style.width = `${data.trust * 100}%`;
    }
    
    // Pulse effect on orb if tension is present
    if (data.tension !== undefined) {
        visualTension = data.tension;
    } else if (data.kinetics !== undefined) {
        // Derive synthetic tension from kinetics (motion)
        const k = data.kinetics / 20.0; // Normalized roughly
        lastKinetics = Math.max(lastKinetics * 0.9, k);
        visualTension = Math.max(visualTension, lastKinetics * 0.5);
    }

    document.getElementById('tension-val').innerText = visualTension.toFixed(2);
    document.getElementById('tension-fill').style.width = `${Math.min(100, visualTension * 100)}%`;
    
    // Change orb color based on tension (blue to red)
    const color = new THREE.Color();
    // High sensitivity for visual display: Boost 5x but allow mixing with audio
    const displayTension = Math.min(1.0, visualTension * 5.0); 
    
    // Phase 10: Color Interpolation (Blue -> Magenta -> Red)
    // Blue (0, 0.5, 1) -> Red (1, 0, 0)
    color.setRGB(
        displayTension, 
        0.5 * (1 - displayTension), 
        (1 - displayTension)
    );
    
    if (globe) {
        globe.material.color = color;
        globe.material.emissive = color;
        globe.material.emissiveIntensity = 0.3 + (displayTension * 0.7);
    }
}

const audioBars = document.getElementById('audio-bars');
// Create bars once
if (audioBars.children.length === 0) {
    for (let i = 0; i < 20; i++) {
        const bar = document.createElement('div');
        bar.className = 'bar';
        audioBars.appendChild(bar);
    }
}

function updateAudio(rms) {
    const bars = document.querySelectorAll('.bar');
    bars.forEach((bar, i) => {
        const height = Math.random() * rms * 150 + 10;
        bar.style.height = `${Math.min(100, height)}%`;
    });

    // Mix audio into visual tension for the red-shift effect
    // If audio is loud, the orb turns more red/unsettled
    const audioTension = Math.min(1.0, rms * 10.0);
    visualTension = Math.max(visualTension, audioTension * 0.8);

    // Phase 10: Physical Sensitivity - Scale the Orb with audio RMS
    if (globe) {
        const scale = 1.0 + (rms * 3.0); // Slightly more sensitive
        globe.scale.set(scale, scale, scale);
        
        // Sync color immediately if audio energy is high
        const color = new THREE.Color();
        const displayTension = Math.min(1.0, visualTension * 5.0);
        color.setRGB(displayTension, 0.5 * (1 - displayTension), 1 - displayTension);
        globe.material.color = color;
        globe.material.emissive = color;
    }
    
    // Decay visual tension slowly
    visualTension *= 0.98;
}

function updateVision(b64) {
    const canvas = document.getElementById('vision-canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    
    // Maintain actual image aspect ratio, CSS object-fit will scale fit
    img.onload = () => {
        // Fix resolution to actual image dimensions
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

    // Add to chat history
    const history = document.getElementById('event-log');
    if (history) {
        const msgDiv = document.createElement('div');
        msgDiv.className = `chat-message kernel ${dissonance ? 'dissonance' : ''}`;
        msgDiv.innerText = text;
        history.appendChild(msgDiv);
        history.scrollTop = history.scrollHeight;
    }
    
    // Phase 12.3: Show/Hide Dissonance Badge
    const badge = document.getElementById('dissonance-badge');
    if (dissonance) {
        badge.classList.remove('hidden');
    } else {
        badge.classList.add('hidden');
    }
}

// Start
window.addEventListener('load', () => {
    initOrb();
    initWebSocket();
    
    // Setup Chat Input
    const sendBtn = document.getElementById('chat-send');
    const chatInput = document.getElementById('chat-input');
    const history = document.getElementById('event-log');

    function sendMessage() {
        if (!chatInput.value.trim() || !ws || ws.readyState !== WebSocket.OPEN) return;
        const text = chatInput.value.trim();
        
        // Render user message
        const msgDiv = document.createElement('div');
        msgDiv.className = 'chat-message';
        msgDiv.innerText = `You: ${text}`;
        history.appendChild(msgDiv);
        history.scrollTop = history.scrollHeight;

        // Send to Kernel (Chat format payload)
        // Wait, the chat sever only supports receiving JSON currently for specific routes or raw text?
        // Actually, the server handles chat properly through the websocket if needed, 
        // we will send a basic interaction structure.
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
    
    // Update Clock
    setInterval(() => {
        const now = new Date();
        document.getElementById('time-val').innerText = now.toTimeString().split(' ')[0];
    }, 1000);
});

window.addEventListener('resize', () => {
    camera.aspect = orbContainer.offsetWidth / orbContainer.offsetHeight;
    camera.updateProjectionMatrix();
    renderer.setSize(orbContainer.offsetWidth, orbContainer.offsetHeight);
});
