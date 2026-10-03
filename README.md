# HoYoLAB Auto Daily Check-in 🎁

Automatización del check-in diario para **Genshin Impact** y **Zenless Zone Zero (ZZZ)** usando GitHub Actions y la librería `genshin.py`.

---

## ⚙️ Configuración inicial

### 1. Obtener tus Cookies de HoYoLAB
1. Inicia sesión en [hoyolab.com](https://www.hoyolab.com).
2. Abre las herramientas de desarrollador presionando <kbd>F12</kbd> (o clic derecho -> **Inspeccionar**).
3. Ve a la pestaña **Consola** (Console).
4. Pega el siguiente comando y presiona <kbd>Enter</kbd>:
   ```javascript
   document.cookie
   ```
5. Copia todo el texto generado (comienza con comillas y contiene `ltuid_v2=...; ltoken_v2=...`).

### 2. Configurar el Secret en GitHub
1. En tu repositorio, entra en **Settings** > **Secrets and variables** > **Actions**.
2. Haz clic en **New repository secret**.
3. **Nombre:** `HOYOLAB_COOKIE`
4. **Secret:** Pega todo el texto de las cookies que copiaste en el paso anterior.
5. *(Opcional)* Si quieres recibir notificaciones en Discord, crea otro secret llamado `DISCORD_WEBHOOK` con la URL del Webhook de tu canal.

---

## 🚀 Probar que funciona
1. En tu repositorio, ve a la pestaña **Actions**.
2. En la lista izquierda, haz clic en **HoYoLAB Daily Check-in**.
3. Haz clic en el botón **Run workflow** -> **Run workflow**.
4. Espera unos segundos, entra en la ejecución y confirma que se hayan reclamado las recompensas con éxito.

---

## ⏰ Horario de ejecución
El flujo se ejecutará automáticamente todos los días a las **13:00 (1:00 PM) UTC-3** (hora de Argentina, Chile, Uruguay).
