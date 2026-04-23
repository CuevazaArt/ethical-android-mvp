/**
 * Nomad Media Engine (Bloque F.2: Cursor)
 * Captures Camera and Mic, downsamples to required backend specs
 * (16kHz PCM audio, 640x480 JPEG video), and injects into WebSocket.
 */

let mediaStream = null;
let audioContext = null;
let videoInterval = null;
const FRAME_RATE = 5; // 5 FPS is enough for situational awareness without melting the LAN
const TARGET_SAMPLE_RATE = 16000;

// ── Bloque 13.2: VAD (Voice Activity Detection) ──────────────────────────────
// Prevents sending raw PCM noise or triggering STT on background silence.
// Only audio that exceeds the RMS gate for a minimum number of consecutive
// frames is considered "speech"; the bridge is notified of start/end events.
const VAD_RMS_THRESHOLD   = 0.015;  // below = silence (tune per environment)
const VAD_ONSET_FRAMES    = 3;      // consecutive above-threshold frames to declare speech start
const VAD_HANGOVER_FRAMES = 12;     // frames to keep "speaking" after RMS drops below threshold

let _vadAboveCount   = 0;   // consecutive frames above threshold
let _vadHangover     = 0;   // hangover counter (frames after RMS drops)
let _vadSpeaking     = false;

/**
 * Update VAD state machine and return whether audio should be sent now.
 * @param {number} rms - Normalised RMS of current audio frame [0..1]
 * @returns {boolean} true if the frame is classified as "speech"
 */
function vadUpdate(rms) {
    const active = rms >= VAD_RMS_THRESHOLD;

    if (active) {
        _vadHangover = VAD_HANGOVER_FRAMES;
        _vadAboveCount = Math.min(_vadAboveCount + 1, VAD_ONSET_FRAMES + 1);
    } else {
        _vadAboveCount = 0;
        if (_vadHangover > 0) _vadHangover--;
    }

    const wasSpeaking = _vadSpeaking;
    // Latch: once onset fires, hangover alone sustains speech;
    // when not yet speaking, onset still requires ONSET_FRAMES consecutive frames.
    if (!_vadSpeaking) {
        _vadSpeaking = _vadAboveCount >= VAD_ONSET_FRAMES;
    } else {
        _vadSpeaking = _vadHangover > 0;
    }

    // Notify bridge of speech-start / speech-end transitions
    if (!wasSpeaking && _vadSpeaking) {
        if (typeof wsNomad !== 'undefined' && wsNomad && wsNomad.readyState === WebSocket.OPEN) {
            try {
                wsNomad.send(JSON.stringify({ type: "vad_event", payload: { state: "speech_start" } }));
            } catch (_) { /* non-fatal */ }
        }
    } else if (wasSpeaking && !_vadSpeaking) {
        if (typeof wsNomad !== 'undefined' && wsNomad && wsNomad.readyState === WebSocket.OPEN) {
            try {
                wsNomad.send(JSON.stringify({ type: "vad_event", payload: { state: "speech_end" } }));
            } catch (_) { /* non-fatal */ }
        }
    }

    return _vadSpeaking;
}

/** Expose current VAD state for external UI queries. */
function isVadSpeaking() { return _vadSpeaking; }
// ─────────────────────────────────────────────────────────────────────────────

const canvas = document.createElement("canvas");
canvas.width = 320; // Downscale further to keep base64 payloads insanely low latency
canvas.height = 240;
const ctx = canvas.getContext('2d', { willReadFrequently: true });

/**
 * Encodes Float32Array PCM data to 16-bit Int PCM and then to Base64
 */
function encodeAudioToBase64(float32Array) {
    const buffer = new ArrayBuffer(float32Array.length * 2);
    const view = new DataView(buffer);
    for (let i = 0; i < float32Array.length; i++) {
        let s = Math.max(-1, Math.min(1, float32Array[i]));
        view.setInt16(i * 2, s < 0 ? s * 0x8000 : s * 0x7FFF, true);
    }
    const bytes = new Uint8Array(buffer);
    let binary = '';
    for (let i = 0; i < bytes.byteLength; i++) {
        binary += String.fromCharCode(bytes[i]);
    }
    return window.btoa(binary);
}

/**
 * Main routine to ask for permissions and start the loop
 */
async function startSensors() {
    // Bloque 13.1 Security: Check for Secure Context before attempting getUserMedia
    if (!navigator.mediaDevices) {
        let msg = "Browser blocks sensors on insecure (HTTP) LAN IPs.";
        if (!window.isSecureContext) {
            msg = "INSECURE CONTEXT: Browser blocked Camera/Mic. \n\nUse Chrome Flags (unsafely-treat-insecure-origin-as-secure) or HTTPS.";
        }
        console.error(msg);
        alert(msg);
        return;
    }

    try {
        mediaStream = await navigator.mediaDevices.getUserMedia({
            video: { facingMode: 'environment', width: 640, height: 480 },
            audio: {
                echoCancellation: true,
                noiseSuppression: true,
                autoGainControl: true,
                channelCount: 1 // Mono
            }
        });
        
        // ... rest of the successful initialization ...
        UI.videoElement.srcObject = mediaStream;

        // Start frame capture loop
        videoInterval = setInterval(() => {
            if (wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                ctx.drawImage(UI.videoElement, 0, 0, canvas.width, canvas.height);
                const base64Img = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];
                wsNomad.send(JSON.stringify({ type: "vision_frame", payload: { image_b64: base64Img } }));
            }
        }, 1000 / FRAME_RATE);

        audioContext = new (window.AudioContext || window.webkitAudioContext)({ sampleRate: TARGET_SAMPLE_RATE });
        const source = audioContext.createMediaStreamSource(mediaStream);
        const processor = audioContext.createScriptProcessor(4096, 1, 1);
        source.connect(processor);
        processor.connect(audioContext.destination);

        processor.onaudioprocess = (e) => {
            const inputData = e.inputBuffer.getChannelData(0);
            let sumSquares = 0;
            for (let i = 0; i < inputData.length; i++) sumSquares += inputData[i] * inputData[i];
            const rms = Math.sqrt(sumSquares / inputData.length);
            const normalizedVolume = Math.min(1, rms * 5);
            const isSpeech = vadUpdate(rms);

            window.requestAnimationFrame(() => {
                if (window.updateOrbScale) window.updateOrbScale(normalizedVolume);
                // Update Nomad telemetry display
                const telAud = document.getElementById('tel-aud');
                if (telAud) telAud.textContent = rms.toFixed(3);
            });

            if (isSpeech && wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                const b64Audio = encodeAudioToBase64(inputData);
                try {
                    wsNomad.send(JSON.stringify({ type: "audio_pcm", payload: { audio_b64: b64Audio } }));
                } catch (_) {}
            }
        };

        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.onresult = (event) => {
                const result = event.results[event.results.length - 1];
                const transcript = result[0].transcript.trim();
                const confidence = result[0].confidence ?? 1.0;
                if (transcript.length > 0 && confidence > 0.4 && (isVadSpeaking() || _vadHangover > 0)) {
                    if (wsChat && wsChat.readyState === WebSocket.OPEN) {
                        UI.transcript.innerText = `You: ${transcript}`;
                        try { wsChat.send(JSON.stringify({ type: "user_speech", text: transcript, confidence })); } catch (_) {}
                    }
                }
            };
            recognition.onend = () => { try { recognition.start(); } catch(e){} };
            recognition.start();
        }

        console.log("Sensors online.");
        UI.transcript.innerText = "Sensors Online. Environment mapped.";

    } catch (err) {
        console.error("No se pudo acceder a los sensores: ", err);
        alert(`Sensor Error: ${err.name || 'Unknown'}\n${err.message}\n\nTroubleshoot:\n1. Ensure HTTPS or Chrome Flags bypass.\n2. Check browser site permissions.`);
        setAppAffectState('calm');
    }
}

function stopSensors() {
    if (videoInterval) clearInterval(videoInterval);
    if (audioContext) audioContext.close();
    if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
    }
}
