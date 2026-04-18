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
    btnInstall: document.getElementById('btn-install'),
    batterySpan: document.getElementById('telemetry-battery'),
    transcript: document.getElementById('charm-transcript'),
    videoElement: document.getElementById('hidden-video'),
};

let wsChat = null;
let wsNomad = null;
let isConnected = false;

// We will default to localhost for DEV, but it should be set to the PC's actual LAN IP
const PC_IP = window.location.hostname || "127.0.0.1";
const WS_PORT = window.location.port || "8765"; // Use current port or default to 8765

/**
 * Battery & Kinetic Telemetry (Replaced Temp due to browser security)
 */
let lastKineticPulse = 0;
if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
        battery.addEventListener('levelchange', () => {
            if(wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                wsNomad.send(JSON.stringify({ type: "telemetry", payload: { battery: battery.level } }));
            }
        });
    });
}
window.addEventListener('devicemotion', (event) => {
    // Only send kinetic telemetry if connected
    if(wsNomad && wsNomad.readyState === WebSocket.OPEN) {
        let acc = event.acceleration;
        if(acc) {
            let magnitude = Math.sqrt((acc.x||0)**2 + (acc.y||0)**2 + (acc.z||0)**2);
            // Throttle to 1 Hz to avoid flooding
            let now = Date.now();
            if(now - lastKineticPulse > 1000) {
                wsNomad.send(JSON.stringify({ type: "telemetry", payload: { kinetics: magnitude } }));
                lastKineticPulse = now;
            }
        }
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
function connectKernel() {
    UI.statusText.innerText = "Connecting...";
    
    // Determine protocol: WSS for HTTPS, WS for HTTP
    const protocol = window.location.protocol === 'https:' ? 'wss:' : 'ws:';
    
    try {
        wsChat = new WebSocket(`${protocol}//${PC_IP}:${WS_PORT}/ws/chat`);
        
        wsChat.onopen = () => {
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
        };

        wsChat.onmessage = (event) => {
            try {
                const msg = JSON.parse(event.data);
                // Claude's domain (F.4): detailed message handling
                if (msg.role === 'android') {
                    UI.transcript.innerText = msg.content;
                }
                
                // If a physical veto occurs
                if (msg.type === 'veto') {
                    setAppAffectState('alert');
                    UI.transcript.innerText = "KERNEL LOCK: Threat detected.";
                }

                // Phase 11: Ouroboros TTS
                if (msg.type === 'kernel_voice') {
                    UI.transcript.innerText = `Kernel: ${msg.text}`;
                    if ('speechSynthesis' in window) {
                        const utterance = new SpeechSynthesisUtterance(msg.text);
                        // Try to find a robotic or english voice, fallback to default
                        const voices = window.speechSynthesis.getVoices();
                        const voice = voices.find(v => v.name.includes("Google") || v.name.includes("English")) || voices[0];
                        if(voice) utterance.voice = voice;
                        window.speechSynthesis.speak(utterance);
                    }
                }

            } catch(e) {
                console.error("Parse error on message", e);
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
        };

        // Antigravity & Cursor - add wsNomad initialization for the sensor stream
        wsNomad = new WebSocket(`${protocol}//${PC_IP}:${WS_PORT}/ws/nomad`);
        wsNomad.onopen = () => { console.log('Nomad Sensory Bridge established'); };

    } catch (e) {
        alert("Cannot connect to the Ethos Kernel. Are you on the same Wi-Fi?");
        UI.statusText.innerText = "Error";
    }
}

// Event Listeners
UI.btnConnect.addEventListener('click', connectKernel);

UI.btnStream.addEventListener('click', () => {
    setAppAffectState('active'); // Transition UI immediately to Active State
    startSensors(); // Defined in media_engine.js
});

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

if ('serviceWorker' in navigator) {
    window.addEventListener('load', () => {
        navigator.serviceWorker.register('./sw.js')
            .then(reg => console.log('Nomad Service Worker registered', reg))
            .catch(err => console.error('SW block:', err));
    });
}

// Initialization
console.log("Nomad PWA V2.1 Initialized. Waiting for connection.");
