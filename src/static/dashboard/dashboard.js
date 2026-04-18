// ════ Ethos Kernel | L0 Dashboard Controller ════

let scene, camera, renderer, globe;
let ws;
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
            updateThoughts(msg.payload.text);
            break;
    }
}

function updateTelemetry(data) {
    if (data.battery) document.getElementById('bat-val').innerText = `${Math.round(data.battery)}%`;
    if (data.temp) document.getElementById('temp-val').innerText = `${Math.round(data.temp)}°C`;
    
    // Pulse effect on orb if tension is high
    if (data.tension) {
        const t = data.tension;
        document.getElementById('tension-val').innerText = t.toFixed(2);
        document.getElementById('tension-fill').style.width = `${t * 100}%`;
        
        // Change orb color based on tension
        const hue = 220 - (t * 100); // 220 (blue) to 120 (red/green)
        globe.material.color.setHSL(hue / 360, 0.7, 0.5);
        globe.material.emissiveIntensity = 0.5 + t;
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
}

function updateVision(b64) {
    const canvas = document.getElementById('vision-canvas');
    const ctx = canvas.getContext('2d');
    const img = new Image();
    img.onload = () => {
        canvas.width = img.width;
        canvas.height = img.height;
        ctx.drawImage(img, 0, 0);
    };
    img.src = `data:image/jpeg;base64,${b64}`;
}

function updateThoughts(text) {
    const el = document.getElementById('thought-stream');
    el.innerText = text;
}

// Start
window.addEventListener('load', () => {
    initOrb();
    initWebSocket();
    
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
