# README — HTTPS para Nomad PWA en LAN

## Por qué HTTPS es obligatorio

Los navegadores móviles (Chrome/Android, Safari/iOS) **bloquean** las siguientes APIs en conexiones HTTP de LAN:

| API | Requiere HTTPS en LAN |
|-----|-----------------------|
| `SpeechRecognition` | ✅ |
| `getUserMedia` (micrófono/cámara) | ✅ |
| `DeviceOrientation` / `DeviceMotion` | ✅ |
| `navigator.wakeLock` | ✅ |

La única excepción es `localhost` — para cualquier IP de LAN (ej. `192.168.1.65`), HTTPS es **mandatorio**.

---

## Paso 1 — Generar el certificado auto-firmado

```bash
python scripts/gen_cert.py --ip 192.168.1.65
```

Salida esperada:
```
✅ Cert generado: certs/server.crt
   SHA256 : AB:CD:EF:...
   Válido hasta: 2026-04-24
   SAN   : IP:192.168.1.65, DNS:localhost, IP:127.0.0.1
```

> **Idempotente:** si el cert es válido (>7 días restantes), no regenera. Usa `--force` para forzar.

El script genera:
- `certs/server.key` — clave RSA-2048 privada (no subir al repo)
- `certs/server.crt` — certificado X.509 con SAN

---

## Paso 2 — Arrancar el servidor en HTTPS

```bash
uvicorn src.server.app:app \
  --host 0.0.0.0 \
  --port 8443 \
  --ssl-keyfile certs/server.key \
  --ssl-certfile certs/server.crt
```

En Windows PowerShell:
```powershell
$env:PYTHONIOENCODING="utf-8"
uvicorn src.server.app:app --host 0.0.0.0 --port 8443 --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt
```

El servidor queda disponible en:
- `https://localhost:8443/` — chat desktop
- `https://localhost:8443/dashboard` — telemetría
- `https://192.168.1.65:8443/nomad` — **Nomad PWA desde móvil**

---

## Paso 3 — Acceder desde el móvil

1. Asegúrate de que el PC y el móvil estén en la **misma red WiFi**
2. Abre en el móvil: **`https://192.168.1.65:8443/nomad`**
3. El navegador mostrará una advertencia de cert no confiable → es normal

---

## Paso 4 — Aceptar el certificado auto-firmado

### Android (Chrome)
1. Aparece "Tu conexión no es privada"
2. Toca **Configuración avanzada**
3. Toca **Acceder a 192.168.1.65 (sitio no seguro)**

### Android — instalar como CA de confianza (elimina el aviso permanentemente)
1. Copia `certs/server.crt` al móvil (AirDrop, cable, Google Drive)
2. **Ajustes → Seguridad → Más ajustes de seguridad → Instalar desde almacenamiento**
3. Elige el archivo `.crt` → Dale un nombre (ej. "Ethos Kernel") → Confirma
4. El cert aparecerá en Ajustes → Seguridad → Credenciales de usuario

### iOS (Safari)
1. Copia `certs/server.crt` al iPhone (AirDrop o correo)
2. **Ajustes → General → VPN y administración de dispositivos → [nombre del perfil]** → Instalar
3. **Ajustes → General → Información → Configuración de confianza de certificados** → Activa el cert

---

## Paso 5 — Verificar que los sensores funcionan

Una vez conectado por HTTPS:
- El orb del Nomad PWA debe mostrar un anillo verde pulsante (mic activo)
- El campo de texto muestra transcripción en vivo al hablar
- Los valores de kinética y batería aparecen en la barra de telemetría

---

## Referencia rápida

```bash
# Generar cert (una vez)
python scripts/gen_cert.py

# Servidor HTTP (desarrollo local, sin sensores en LAN)
uvicorn src.server.app:app --host 0.0.0.0 --port 8000

# Servidor HTTPS (producción LAN, todos los sensores activos)
uvicorn src.server.app:app --host 0.0.0.0 --port 8443 --ssl-keyfile certs/server.key --ssl-certfile certs/server.crt
```
