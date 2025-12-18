# 🎨 Setup de Streamlit Cloud

Guía paso a paso para deployar el dashboard en Streamlit Cloud (100% gratuito).

## ⏱️ Tiempo estimado: 3 minutos

## 📋 Requisitos

- Cuenta de GitHub
- Proyecto de Supabase configurado ([SETUP_SUPABASE.md](SETUP_SUPABASE.md))
- Credenciales de Supabase (Project URL y anon key)

## 🚀 Pasos

### 1. Fork del Repositorio

1. Ir al repositorio original: [github.com/TU_USUARIO/expense-tracker](https://github.com/TU_USUARIO/expense-tracker)
2. Hacer clic en **Fork** (esquina superior derecha)
3. Esperar que GitHub copie el repositorio a tu cuenta

![GitHub Fork](../assets/screenshots/github-fork.png)

### 2. Crear Cuenta en Streamlit Cloud

1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Hacer clic en **Sign up**
3. Autenticarse con **GitHub**
4. Autorizar a Streamlit Cloud

![Streamlit Login](../assets/screenshots/streamlit-login.png)

### 3. Crear Nueva App

1. Hacer clic en **New app**
2. Completar formulario:
   - **Repository**: Seleccionar tu fork `TU_USUARIO/expense-tracker`
   - **Branch**: `main`
   - **Main file path**: `dashboard/streamlit_app.py`
   - **App URL** (opcional): Personalizar URL

![Streamlit New App](../assets/screenshots/streamlit-new-app.png)

### 4. Configurar Secrets

**ANTES de hacer deploy**, configurar variables de entorno:

1. Hacer clic en **Advanced settings**
2. En la sección **Secrets**, pegar:

```toml
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"
```

**⚠️ Reemplazar** `url` y `key` con tus credenciales de Supabase.

![Streamlit Secrets](../assets/screenshots/streamlit-secrets.png)

### 5. Deploy

1. Hacer clic en **Deploy**
2. Esperar 2-3 minutos mientras Streamlit instala dependencias
3. Ver logs en tiempo real

![Streamlit Deploying](../assets/screenshots/streamlit-deploying.png)

**✅ Éxito**: Cuando veas tu app corriendo.

### 6. Verificar Dashboard

1. Tu app estará disponible en: `https://tu-app.streamlit.app`
2. Deberías ver la pantalla de login
3. Crear cuenta o iniciar sesión

![Dashboard Login](../assets/screenshots/dashboard-login.png)

## 🔧 Configuración Local (Opcional)

Para desarrollar localmente antes de deployar:

### 1. Clonar tu Fork

```bash
git clone https://github.com/TU_USUARIO/expense-tracker.git
cd expense-tracker/dashboard
```

### 2. Crear Virtual Environment

```bash
python -m venv venv

# Windows
venv\Scripts\activate

# Linux/Mac
source venv/bin/activate
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

### 4. Configurar Secrets Localmente

```bash
# Crear directorio
mkdir .streamlit

# Copiar template
cp secrets.toml.example .streamlit/secrets.toml

# Editar con tus credenciales
nano .streamlit/secrets.toml
```

Contenido de `.streamlit/secrets.toml`:
```toml
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"
key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"
```

### 5. Ejecutar Localmente

```bash
streamlit run streamlit_app.py
```

Abrir navegador en: `http://localhost:8501`

## 🔄 Actualizar Dashboard

### Deploy Automático

Streamlit Cloud detecta cambios en tu repositorio:

1. Hacer cambios en tu código
2. Commit y push a GitHub:
   ```bash
   git add .
   git commit -m "Update: nueva funcionalidad"
   git push origin main
   ```
3. Streamlit Cloud re-deploya automáticamente

### Deploy Manual

Si el auto-deploy falla:

1. Ir a [share.streamlit.io](https://share.streamlit.io)
2. Encontrar tu app
3. Hacer clic en **⋮** → **Reboot app**

## 🐛 Troubleshooting

### Error: "No module named 'supabase'"

**Causa**: `requirements.txt` no está siendo detectado.

**Solución**:
1. Verificar que `dashboard/requirements.txt` existe
2. En Streamlit Cloud, ir a **Advanced settings**
3. Python version: `3.10`
4. Reboot app

### Error: "st.secrets has no attribute 'supabase'"

**Causa**: Secrets no configurados correctamente.

**Solución**:
1. Ir a **App settings** → **Secrets**
2. Verificar formato TOML:
   ```toml
   [supabase]
   url = "..."
   key = "..."
   ```
3. Sin comillas extras ni espacios

### App se queda "Cargando..."

**Causa**: Error en el código o conexión a Supabase.

**Solución**:
1. Ver logs en Streamlit Cloud
2. Verificar credenciales de Supabase
3. Test de conexión:
   ```python
   from supabase import create_client
   client = create_client(url, key)
   print(client.table('transactions').select('*').execute())
   ```

### App muy lenta

**Causa**: Free tier tiene recursos limitados.

**Solución**:
1. Optimizar queries (usar `select('*')` solo cuando necesario)
2. Agregar caching con `@st.cache_data`
3. Limitar cantidad de datos mostrados

Ejemplo de caching:
```python
@st.cache_data(ttl=600)  # Cache por 10 min
def get_transactions():
    return client.table('transactions').select('*').execute()
```

## 📊 Monitoreo

### Ver Logs

1. Ir a tu app en Streamlit Cloud
2. Hacer clic en **Manage app**
3. Ver **Logs** en tiempo real

### Analíticas (Futuro)

Streamlit Cloud no incluye analytics en free tier. Para trackear uso:

1. Agregar Google Analytics
2. Usar [streamlit-analytics](https://github.com/jrieke/streamlit-analytics)

## 🔐 Seguridad

### Secrets

- Nunca hacer commit de `.streamlit/secrets.toml`
- Verificar que está en `.gitignore`
- Rotar keys si se exponen

### HTTPS

Streamlit Cloud usa HTTPS automáticamente:
- `https://tu-app.streamlit.app` ✅
- `http://tu-app.streamlit.app` ❌ (redirige a HTTPS)

### Limitar Acceso (Opcional)

Para apps privadas:

1. Usar Supabase Auth
2. Implementar password en `streamlit_app.py`:
   ```python
   if st.session_state.get('authenticated'):
       # Mostrar dashboard
   else:
       # Mostrar login
   ```

## 📚 Recursos

- [Documentación Streamlit](https://docs.streamlit.io)
- [Streamlit Cloud Docs](https://docs.streamlit.io/streamlit-community-cloud)
- [Streamlit Components](https://streamlit.io/components)

## ✅ Checklist

- [ ] Fork del repositorio creado
- [ ] Cuenta de Streamlit Cloud creada
- [ ] Nueva app configurada
- [ ] Secrets agregados correctamente
- [ ] App deployada sin errores
- [ ] Dashboard accesible en URL pública
- [ ] Login funcionando
- [ ] (Opcional) Desarrollo local configurado

## 🎉 Siguiente Paso

Continuar con [SETUP_SCRAPER.md](SETUP_SCRAPER.md) para configurar el scraper de tarjetas.
