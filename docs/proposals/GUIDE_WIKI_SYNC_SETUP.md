# 📖 Guía de Configuración: Sincronización Automática de la Wiki

Para que la documentación técnica (ADRs, Propuestas, Roadmaps) sea visible en la **GitHub Wiki** de manera automática cada vez que haces `git push`, sigue estos pasos:

## 1. Crear un Personal Access Token (PAT)
GitHub Actions necesita un permiso especial para escribir en el repositorio de la Wiki (que es técnicamente un repositorio oculto separado).

1. Ve a **Settings** de tu cuenta personal de GitHub (arriba a la derecha).
2. Baja hasta **Developer settings** (en la barra lateral izquierda).
3. Selecciona **Personal access tokens** -> **Tokens (classic)**.
4. Haz clic en **Generate new token (classic)**.
5. Ponle un nombre (ej: `Wiki Sync Antigravity`).
6. Selecciona el scope **`repo`** (esto permite escribir en los repos de la organización/usuario, incluyendo la wiki).
7. Haz clic en **Generate token** y **COPIA EL TOKEN** (no lo volverás a ver).

## 2. Configurar el Secreto en el Repositorio
Ahora debemos darle ese token al Ethos Kernel de forma segura.

1. Ve a la página principal de tu repositorio `ethical-android-mvp`.
2. Haz clic en **Settings** (la pestaña superior del repo).
3. En la barra lateral, ve a **Secrets and variables** -> **Actions**.
4. Haz clic en **New repository secret**.
5. **Name:** `WIKI_SYNC_TOKEN`
6. **Secret:** (Pega el token que copiaste en el paso anterior).
7. Haz clic en **Add secret**.

## 3. Limpieza de Flujos Duplicados
Actualmente hay dos archivos de configuración que pueden entrar en conflicto. Vamos a dejar solo el oficial.

1. Borra el archivo `.github/workflows/wiki-sync.yml`.
2. Asegúrate de que `.github/workflows/wiki_sync.yml` (con guion bajo) esté presente.

## 4. Disparar la Sincronización
La sincronización se activa automáticamente al empujar cambios a las carpetas `docs/**`.

```bash
git add .
git commit -m "docs: activating automated wiki sync"
git push origin main
```

## 5. Verificar Resultado
1. Ve a la pestaña **Actions** de tu repositorio.
2. Deberías ver un workflow llamado **Wiki Sync (Nomadic Docs)** ejecutándose.
3. Una vez termine en verde, ve a la pestaña **Wiki** de tu repositorio. ¡Toda tu arquitectura y propuestas deberían estar ahí organizadas!

---
> [!TIP]
> Si deseas forzar una sincronización sin cambiar archivos, puedes ir a **Actions** -> **Wiki Sync** -> **Run workflow** manualmente en la interfaz de GitHub.
