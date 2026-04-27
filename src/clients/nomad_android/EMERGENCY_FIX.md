# 🚨 PROMPT DE EMERGENCIA — Pega esto a Android Studio

---

**El chat no funciona. El backend está vivo. Necesito que diagnostiques y arregles.**

## Paso 1: Sincroniza el código

Ejecuta esto en la terminal de Android Studio (Terminal tab, abajo):

```bash
cd c:\Users\lexar\Desktop\ethos-kernel-antigravity
git stash
git pull origin main
```

Si te dice "Already up to date", el código ya está sincronizado.
Si te dice conflictos, ejecuta `git stash drop` y continúa.

## Paso 2: Verifica que tienes el código correcto

Abre `app/src/main/java/com/ethos/nomad/ui/ChatViewModel.kt` y confirma que ves esto cerca de la línea 41:

```kotlin
private const val WS_URL = "ws://10.0.2.2:8000/ws/chat"
```

Si NO lo ves, o ves otra URL, el problema es que no tienes nuestro código. Haz `git checkout -- .` para restaurar.

## Paso 3: Verifica que el emulador tiene acceso a la red

En la terminal de Android Studio:

```bash
adb shell ping -c 3 10.0.2.2
```

Si responde → la red funciona.
Si NO responde → el emulador no tiene conectividad. Verifica que el emulador tiene "Internet" habilitado en su configuración.

## Paso 4: Verifica el Logcat

1. Corre la app en el emulador (Run ▶️)
2. Abre la pestaña **Logcat** (abajo)
3. En el filtro escribe: `ChatViewModel`
4. Copia TODA la salida que ves y pégala en SYNC.md bajo la sección 📥

Lo que espero ver:
- `WebSocket connected to ws://10.0.2.2:8000/ws/chat` → ✅ funciona
- `WebSocket failure: ...` → ❌ error de conexión (copia el mensaje)
- Nada → ❌ el ViewModel no se instancia

## Paso 5: Verifica que el servidor responde

En la terminal de Android Studio:

```bash
adb shell curl http://10.0.2.2:8000/api/ping
```

Debe devolver: `{"pong":true,"uptime_s":...}`

## Paso 6: Si nada funciona, prueba cleartext

Puede ser que Android bloquee tráfico HTTP sin TLS. Verifica que `AndroidManifest.xml` tiene:

```xml
<application
    android:usesCleartextTraffic="true"
    ...>
```

Si NO tiene `android:usesCleartextTraffic="true"`, **agrégalo**. Este es el error más común con WebSockets en Android sobre HTTP (no HTTPS).

## Paso 7: Reporta

Después de cada paso, haz commit y push:

```bash
git add .
git commit -m "V2.82: AS diagnostic report"
git push origin main
```

O al menos copia tu diagnóstico y dáselo al usuario para que me lo pase.

---

**RECORDATORIO: El servidor backend está VIVO en el puerto 8000. El problema es 100% del lado Android.**
