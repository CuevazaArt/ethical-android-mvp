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
let lastBatteryLevel = null;

if ('getBattery' in navigator) {
    navigator.getBattery().then(battery => {
        lastBatteryLevel = battery.level;
        const sendBat = () => {
            if(wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                // Proxy for 'Temperature' (browser block workaround): High drain scale
                let tempProxy = 40 + (1.0 - battery.level) * 10; 
                wsNomad.send(JSON.stringify({ 
                    type: "telemetry", 
                    payload: { 
                        battery: battery.level,
                        is_charging: battery.charging,
                        temp: tempProxy // Simulated thermal state based on drain
                    } 
                }));
            }
        };
        battery.addEventListener('levelchange', sendBat);
        battery.addEventListener('chargingchange', sendBat);
        sendBat();
    });
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
    if(wsNomad && wsNomad.readyState === WebSocket.OPEN) {
        let acc = event.acceleration;
        if(acc) {
            let magnitude = Math.sqrt((acc.x||0)**2 + (acc.y||0)**2 + (acc.z||0)**2);
            let now = Date.now();
            
            // Phase 12 Hardening: High-intensity impact detection
            if(magnitude > 15) { // Roughly > 1.5G spike
                wsNomad.send(JSON.stringify({ type: "telemetry", payload: { kinetics: magnitude, impact: true } }));
                lastKineticPulse = now;
            } else if(now - lastKineticPulse > 1000) {
                // Normal heartbeat telemetry
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
                
                if (msg.type === 'veto') {
                    setAppAffectState('alert');
                    UI.transcript.innerText = "KERNEL LOCK: Threat detected.";
                }

                if (msg.type === 'ping') {
                    console.debug("Nomad: Keep-alive ping from server.");
                    // Optional: Send a tiny telemetry pulse back
                }

                if (msg.type === 'thought') {
                    // Phase 12.3: Visual hint for dissonance in PWA
                    if (msg.payload.dissonance) {
                        UI.transcript.classList.add('dissonance-active');
                    } else {
                        UI.transcript.classList.remove('dissonance-active');
                    }
                }

                // Phase 12: Ouroboros TTS with Lip-sync
                if (msg.type === 'kernel_voice') {
                    UI.transcript.innerText = `Kernel: ${msg.text}`;
                    if ('speechSynthesis' in window) {
                        const utterance = new SpeechSynthesisUtterance(msg.text);
                        const voices = window.speechSynthesis.getVoices();
                        // Priority voices for Ethos personality
                        const preferred = voices.find(v => v.name.includes("Male") || v.name.includes("UK English")) || voices[0];
                        if(preferred) utterance.voice = preferred;
                        
                        utterance.onstart = () => {
                            UI.orb.classList.add('speaking');
                            // Notify back to NomadBridge if needed (Phase 12.1)
                        };
                        utterance.onend = () => {
                            UI.orb.classList.remove('speaking');
                        };
                        window.speechSynthesis.speak(utterance);
                    }
                }

                // Phase 10.2: Haptic Feedback Loop
                if (msg.type === 'haptic_feedback') {
                    console.log("Nomad: Haptic Pulse received", msg.payload);
                    const plans = msg.payload.haptics || [];
                    plans.forEach(plan => {
                        if (plan.type === 'vibrate' && plan.pattern && navigator.vibrate) {
                            navigator.vibrate(plan.pattern);
                        }
                    });
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
        wsNomad.onopen = () => { 
            console.log('Nomad Sensory Bridge established');
            // Heavy Heartbeat (Fase 12.2)
            setInterval(() => {
               if(wsNomad.readyState === WebSocket.OPEN) {
                   wsNomad.send(JSON.stringify({ type: "telemetry", payload: { heartbeat: true } }));
               }
            }, 15000);
        };

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
