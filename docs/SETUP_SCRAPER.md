# 🤖 Setup del Scraper

Guía paso a paso para configurar el scraper de tarjetas de crédito (corre en tu PC local).

## ⏱️ Tiempo estimado: 7 minutos

## 📋 Requisitos

- Python 3.10 o superior
- Proyecto de Supabase configurado ([SETUP_SUPABASE.md](SETUP_SUPABASE.md))
- Credenciales de tus bancos (usuario y password)
- Windows, Linux o macOS

## 🚀 Pasos

### 1. Clonar el Repositorio

```bash
# Clonar tu fork
git clone https://github.com/TU_USUARIO/expense-tracker.git
cd expense-tracker/scraper
```

### 2. Crear Virtual Environment

```bash
# Crear venv
python -m venv venv

# Activar venv
# Windows (CMD)
venv\Scripts\activate

# Windows (PowerShell)
venv\Scripts\Activate.ps1

# Linux/Mac
source venv/bin/activate
```

Deberías ver `(venv)` en tu terminal.

### 3. Instalar Dependencias

```bash
# Instalar librerías Python
pip install -r requirements.txt

# Instalar navegador Chromium para Playwright
playwright install chromium
```

**⏳ Esperar 1-2 minutos** mientras descarga Chromium (~100 MB).

### 4. Configurar Variables de Entorno

```bash
# Copiar template
cp .env.example .env

# Editar con tus credenciales
# Windows
notepad .env

# Linux/Mac
nano .env
```

Contenido de `.env`:
```env
# Supabase
SUPABASE_URL=https://xxxxxxxxxxxxx.supabase.co
SUPABASE_KEY=eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx

# BBVA (opcional)
BBVA_USERNAME=tu_usuario_bbva
BBVA_PASSWORD=tu_password_bbva

# Galicia (opcional)
GALICIA_USERNAME=tu_usuario_galicia
GALICIA_PASSWORD=tu_password_galicia
```

**⚠️ IMPORTANTE**:
- Reemplazar con tus credenciales reales
- Este archivo **NUNCA** se sube a GitHub (está en `.gitignore`)

### 5. Exportar Cookies de los Bancos

El scraper necesita cookies para mantener la sesión:

#### 5.1. BBVA Visa

```bash
python run.py export-cookies --bank bbva
```

**Pasos**:
1. Se abrirá navegador de Chromium
2. Ingresar manualmente a tu cuenta de BBVA
3. Navegar hasta "Mis Tarjetas" o "Resumen"
4. Presionar `Enter` en la terminal
5. Cookies se guardan automáticamente en `.cookies/bbva.json`

#### 5.2. Galicia Visa y Amex

```bash
python run.py export-cookies --bank galicia
```

**Pasos**:
1. Se abrirá navegador de Chromium
2. Ingresar manualmente a tu cuenta de Galicia
3. Navegar hasta "Tarjetas"
4. Presionar `Enter` en la terminal
5. Cookies se guardan automáticamente en `.cookies/galicia.json`

**✅ Verificar**: Deberías tener 2 archivos en `.cookies/`:
```
.cookies/
├── bbva.json
└── galicia.json
```

### 6. Primera Ejecución del Scraper

```bash
python run.py scrape
```

**Qué hace**:
1. Carga cookies guardadas
2. Navega a cada banco (headless, sin abrir ventana)
3. Extrae transacciones del último mes
4. Inserta en Supabase (evita duplicados)
5. Muestra resumen en terminal

**Salida esperada**:
```
[INFO] Iniciando scraper...
[INFO] Scrapeando BBVA Visa...
[INFO] ✓ Encontradas 15 transacciones
[INFO] ✓ Insertadas 15 nuevas transacciones
[INFO] Scrapeando Galicia Visa...
[INFO] ✓ Encontradas 8 transacciones
[INFO] ✓ Insertadas 8 nuevas transacciones
[INFO] Scrapeando Galicia Amex...
[INFO] ✓ Encontradas 3 transacciones
[INFO] ✓ Insertadas 3 nuevas transacciones
[SUCCESS] Total: 26 transacciones insertadas
```

## 🛠️ Comandos Disponibles

### Scrapear Todas las Tarjetas

```bash
python run.py scrape
```

### Scrapear Banco Específico

```bash
# Solo BBVA
python run.py scrape --bank bbva

# Solo Galicia (Visa + Amex)
python run.py scrape --bank galicia
```

### Modo Verbose (Debug)

```bash
python run.py scrape --verbose
```

Muestra logs detallados y capturas de pantalla en caso de error.

### Ver Ayuda

```bash
python run.py --help
```

## ⏰ Automatización

### Windows (Task Scheduler)

1. Abrir **Task Scheduler**
2. **Create Basic Task**
3. Trigger: **Daily** a las 8:00 AM
4. Action: **Start a program**
   - Program: `C:\ruta\a\venv\Scripts\python.exe`
   - Arguments: `run.py scrape`
   - Start in: `C:\ruta\a\expense-tracker\scraper`

### Linux/Mac (Cron)

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar diario a las 8 AM)
0 8 * * * cd /ruta/a/expense-tracker/scraper && /ruta/a/venv/bin/python run.py scrape
```

### GitHub Actions (Opcional)

Ver `.github/workflows/scraper.yml` para ejecutar en la nube:

**Ventajas**:
- Automático (cron en GitHub)
- No requiere PC encendida

**Desventajas**:
- Cookies deben estar en GitHub Secrets
- Riesgo de seguridad (credenciales en la nube)

**⚠️ NO RECOMENDADO** para información bancaria.

## 🐛 Troubleshooting

### Error: "Cookies expired"

**Causa**: Cookies tienen más de 30 días.

**Solución**:
```bash
# Re-exportar cookies
python run.py export-cookies --bank bbva
python run.py export-cookies --bank galicia
```

### Error: "Could not find element"

**Causa**: El banco cambió la estructura del sitio web.

**Solución**:
1. Ejecutar en modo verbose:
   ```bash
   python run.py scrape --verbose
   ```
2. Revisar capturas en `logs/screenshots/`
3. Actualizar selectores en `banks/bbva.py` o `banks/galicia.py`
4. Abrir issue en GitHub

### Error: "Connection to Supabase failed"

**Causa**: Credenciales incorrectas en `.env`.

**Solución**:
1. Verificar `SUPABASE_URL` y `SUPABASE_KEY` en `.env`
2. Test de conexión:
   ```python
   from dotenv import load_dotenv
   import os
   from supabase import create_client

   load_dotenv()
   client = create_client(
       os.getenv('SUPABASE_URL'),
       os.getenv('SUPABASE_KEY')
   )
   print(client.table('transactions').select('*').limit(1).execute())
   ```

### Scraper muy lento

**Causa**: Navegación headless en sitios complejos.

**Solución**:
- Normal: 30-60 segundos por banco
- Si tarda más de 2 minutos: verificar internet
- Reducir timeouts en `credit_card_scraper.py`

### Captcha en BBVA/Galicia

**Causa**: Detección de bot.

**Solución**:
1. Exportar cookies manualmente (ya logueado)
2. Agregar delays random entre acciones
3. Rotar User-Agent (ya implementado)

## 🔐 Seguridad

### Cookies

- Almacenadas en `.cookies/` (gitignored)
- Cifradas en disco (recomendado)
- Expiración: 30 días aprox.

### Credenciales

- En `.env` (gitignored)
- Nunca en código
- Opción: usar credenciales solo para exportar cookies, luego eliminar

### Capturas de Pantalla

En modo verbose, se guardan screenshots en `logs/screenshots/`:
- Revisar que no contengan información sensible
- Eliminar antes de compartir logs

## 📊 Verificar Datos

Después de scrapear, verificar en:

1. **Supabase Table Editor**:
   - Ver transacciones insertadas

2. **Dashboard Streamlit**:
   - Abrir `https://tu-app.streamlit.app`
   - Deberías ver tus gastos del mes

3. **SQL Query**:
   ```sql
   SELECT COUNT(*) as total, bank
   FROM transactions
   WHERE date >= CURRENT_DATE - INTERVAL '30 days'
   GROUP BY bank;
   ```

## 📚 Recursos

- [Playwright Docs](https://playwright.dev/python/)
- [Supabase Python Client](https://supabase.com/docs/reference/python/introduction)

## ✅ Checklist

- [ ] Python 3.10+ instalado
- [ ] Repositorio clonado
- [ ] Virtual environment creado y activado
- [ ] Dependencias instaladas (`requirements.txt`)
- [ ] Chromium instalado (`playwright install chromium`)
- [ ] `.env` configurado con credenciales de Supabase
- [ ] Cookies exportadas para BBVA
- [ ] Cookies exportadas para Galicia
- [ ] Primera ejecución exitosa (`python run.py scrape`)
- [ ] Transacciones visibles en Supabase
- [ ] (Opcional) Automatización configurada (cron/Task Scheduler)

## 🎉 Próximos Pasos

Tu expense tracker está completo! Ahora puedes:

1. **Usar el Dashboard**: Ver tus gastos en `https://tu-app.streamlit.app`
2. **Configurar Presupuesto**: Ir a página "💰 Presupuesto"
3. **Agregar Gastos Manuales**: Ir a página "➕ Gastos Manuales"
4. **Automatizar**: Configurar cron para scrapear diariamente

## 🤝 Contribuir

Si mejoras el scraper para otros bancos:
1. Crear archivo `banks/tu_banco.py`
2. Abrir Pull Request
3. Ayudar a la comunidad!
