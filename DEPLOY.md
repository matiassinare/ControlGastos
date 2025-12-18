# 🚀 Guía de Deploy - Expense Tracker

## Opción 1: Streamlit Community Cloud (GRATIS y Recomendado)

### Requisitos previos
- Cuenta de GitHub
- Cuenta de Streamlit Cloud (usar tu cuenta de GitHub para crear una)
- Base de datos Supabase configurada

### Paso 1: Subir el código a GitHub

1. **Crear repositorio en GitHub**
   ```bash
   # Inicializar git (si no está inicializado)
   cd "C:\Users\matias.DESKTOP-APTA8FN\Documents\Portfolio_IT\Repositorios\apps\NoName"
   git init

   # Agregar archivos
   git add .
   git commit -m "Initial commit - Expense Tracker App"

   # Conectar con GitHub (crear repo primero en github.com)
   git remote add origin https://github.com/TU_USUARIO/expense-tracker.git
   git branch -M main
   git push -u origin main
   ```

### Paso 2: Configurar Streamlit Cloud

1. Ve a [share.streamlit.io](https://share.streamlit.io)
2. Click en "New app"
3. Seleccioná tu repositorio de GitHub
4. Configurá:
   - **Main file path**: `dashboard/streamlit_app.py`
   - **Python version**: 3.11 (o la que estés usando)

### Paso 3: Configurar Secrets

En Streamlit Cloud, andá a "Advanced settings" → "Secrets" y agregá:

```toml
[supabase]
url = "TU_SUPABASE_URL"
key = "TU_SUPABASE_ANON_KEY"
```

**IMPORTANTE**: No subas el archivo `secrets.toml` a GitHub. Los secrets se configuran directamente en Streamlit Cloud.

### Paso 4: Deploy

Click en "Deploy" y esperá unos minutos. Tu app estará disponible en:
`https://TU_USUARIO-expense-tracker-XXXXX.streamlit.app`

---

## Opción 2: Render (Alternativa GRATIS)

### Paso 1: Crear cuenta en Render
Ve a [render.com](https://render.com) y creá una cuenta

### Paso 2: Crear archivo de configuración

Ya tenés el archivo `requirements.txt` necesario.

### Paso 3: Deploy desde GitHub

1. En Render, click en "New +" → "Web Service"
2. Conectá tu repositorio de GitHub
3. Configurá:
   - **Name**: expense-tracker
   - **Environment**: Python 3
   - **Build Command**: `pip install -r requirements.txt`
   - **Start Command**: `streamlit run dashboard/streamlit_app.py --server.port=$PORT --server.address=0.0.0.0`

### Paso 4: Variables de Entorno

Agregá en "Environment":
- `SUPABASE_URL` = tu URL de Supabase
- `SUPABASE_KEY` = tu key de Supabase

---

## Opción 3: Railway (Alternativa con $5 gratis/mes)

### Paso 1: Crear cuenta
Ve a [railway.app](https://railway.app)

### Paso 2: Deploy
1. Click en "New Project"
2. Seleccioná "Deploy from GitHub repo"
3. Railway detectará automáticamente que es una app Streamlit

### Paso 3: Variables de Entorno
Agregá las mismas variables de Supabase

---

## 🔒 Seguridad

### Archivos que NO deben subirse a GitHub:
- ✅ Ya están en `.gitignore`:
  - `.streamlit/secrets.toml`
  - `dashboard/data/*.json` (datos locales)
  - `.env`
  - Archivos con cookies o credenciales

### Variables que necesitás configurar en producción:
- `SUPABASE_URL`
- `SUPABASE_KEY`

---

## 📝 Checklist Pre-Deploy

- [ ] Código subido a GitHub
- [ ] `requirements.txt` incluido
- [ ] Secrets configurados en la plataforma (NO en el código)
- [ ] Base de datos Supabase configurada y funcionando
- [ ] Migraciones de Supabase ejecutadas (ver SETUP_SUPABASE.md)
- [ ] `.gitignore` configurado correctamente
- [ ] App testeada localmente

---

## 🐛 Troubleshooting

### Error: "Module not found"
- Verificá que todas las dependencias estén en `requirements.txt`
- Revisá que las rutas de import sean correctas

### Error: "Could not connect to Supabase"
- Verificá que los secrets estén configurados correctamente
- Confirmá que la URL y Key de Supabase sean correctas

### La app se reinicia constantemente
- Revisá los logs en la plataforma
- Puede ser un error de import o configuración

### Los datos no persisten
- Verificá la conexión a Supabase
- Los datos locales (JSON) NO persisten en Streamlit Cloud (usá Supabase)

---

## 📊 Monitoreo

Una vez deployado:
- Streamlit Cloud te da métricas de uso gratis
- Podés ver logs en tiempo real
- Configurá notificaciones de errores
