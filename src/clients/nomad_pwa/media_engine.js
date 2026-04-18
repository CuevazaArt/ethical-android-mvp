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

        // 1. Hook up the video
        UI.videoElement.srcObject = mediaStream;

        // Start frame capture loop
        videoInterval = setInterval(() => {
            if (wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                // Draw current frame to canvas, then export as jpeg Base64
                ctx.drawImage(UI.videoElement, 0, 0, canvas.width, canvas.height);
                // get base64 string without the "data:image/jpeg;base64," prefix
                const base64Img = canvas.toDataURL('image/jpeg', 0.6).split(',')[1];
                
                wsNomad.send(JSON.stringify({
                    type: "vision_frame",
                    payload: { image_b64: base64Img }
                }));
            }
        }, 1000 / FRAME_RATE);

        // 2. Hook up the audio
        audioContext = new (window.AudioContext || window.webkitAudioContext)({
            sampleRate: TARGET_SAMPLE_RATE
        });
        const source = audioContext.createMediaStreamSource(mediaStream);
        
        // Use ScriptProcessor (deprecated but universally supported on mobile for raw PCM injection)
        // A real production deployment would use AudioWorklet.
        const processor = audioContext.createScriptProcessor(4096, 1, 1);
        source.connect(processor);
        processor.connect(audioContext.destination);

        processor.onaudioprocess = (e) => {
            if (wsNomad && wsNomad.readyState === WebSocket.OPEN) {
                const inputData = e.inputBuffer.getChannelData(0);
                
                // Audio visualization metric (RMS)
                let sumSquares = 0;
                for (let i = 0; i < inputData.length; i++) {
                    sumSquares += inputData[i] * inputData[i];
                }
                const rms = Math.sqrt(sumSquares / inputData.length);
                const normalizedVolume = Math.min(1, rms * 5); // amplify visual response
                
                // Update UI without blocking the thread
                window.requestAnimationFrame(() => {
                    if (window.updateOrbScale) window.updateOrbScale(normalizedVolume);
                });

                const b64Audio = encodeAudioToBase64(inputData);
                wsNomad.send(JSON.stringify({
                    type: "audio_pcm",
                    payload: { audio_b64: b64Audio }
                }));
            }
        };

        // Phase 11: Ouroboros Native STT
        const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
        if (SpeechRecognition) {
            const recognition = new SpeechRecognition();
            recognition.continuous = true;
            recognition.interimResults = false;
            
            recognition.onresult = (event) => {
                const transcript = event.results[event.results.length - 1][0].transcript.trim();
                console.log("Nomad STT Heard:", transcript);
                if (wsChat && wsChat.readyState === WebSocket.OPEN && transcript.length > 0) {
                    UI.transcript.innerText = `You: ${transcript}`;
                    wsChat.send(JSON.stringify({
                        type: "user_speech",
                        text: transcript
                    }));
                }
            };
            
            recognition.onerror = (e) => console.log('STT Error', e);
            // Auto restart if it stops
            recognition.onend = () => {
                try { recognition.start(); } catch(e){}
            };
            
            recognition.start();
            console.log("Nomad Native STT Active.");
        } else {
            console.warn("SpeechRecognition not supported in this browser fallback needed.");
        }

        console.log("Sensors online. Injecting into NomadBridge.");
        UI.transcript.innerText = "Sensors Online. Environment mapped.";

    } catch (err) {
        console.error("No se pudo acceder a los sensores: ", err);
        alert("Necesitamos acceso a cámara y micrófono para percibir el mundo físico.");
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
