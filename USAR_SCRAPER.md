# 🤖 Cómo Usar el Scraper

## 📋 Prerequisitos

1. **Python 3.10+** instalado
2. **Chromium** de Playwright instalado

## 🚀 Setup Inicial (Solo 1 vez)

### 1. Instalar Dependencias

```bash
cd scraper
pip install -r requirements.txt
playwright install chromium
```

### 2. Verificar Configuración

El archivo `.env` ya está configurado con tus credenciales de Supabase ✅

## 🍪 Exportar Cookies (Primera Vez)

### Opción A: BBVA

```bash
python run.py export-cookies --bank bbva
```

**Qué va a pasar:**
1. Se abre un navegador
2. Ingresás manualmente a tu cuenta de BBVA
3. Navegás hasta "Mis Tarjetas"
4. Presionás ENTER en la terminal
5. Las cookies se guardan automáticamente

### Opción B: Galicia

```bash
python run.py export-cookies --bank galicia
```

**Qué va a pasar:**
1. Se abre un navegador
2. Ingresás manualmente a tu cuenta de Galicia
3. Navegás hasta "Tarjetas"
4. Presionás ENTER en la terminal
5. Las cookies se guardan automáticamente

**✅ Solo necesitás hacer esto 1 vez** (o cuando expiren las cookies, aprox. 30 días)

## 💳 Scrapear Transacciones

### Scrapear Todas las Tarjetas

```bash
python run.py scrape
```

### Scrapear Solo BBVA

```bash
python run.py scrape --bank bbva
```

### Scrapear Solo Galicia

```bash
python run.py scrape --bank galicia
```

### Modo Verbose (Debug)

```bash
python run.py scrape --verbose
```

Muestra logs detallados y abre el navegador visible.

## 📊 Ver Resultados

Después de scrapear:

1. **En la terminal** verás un resumen:
   ```
   📊 RESUMEN DE SCRAPING
   ══════════════════════════════════════

   BBVA Visa:
     ✓ Transacciones encontradas: 15
     ✓ Nuevas insertadas: 15
     ✓ Duplicadas (omitidas): 0

   Galicia (Visa + Amex):
     ✓ Transacciones encontradas: 8
     ✓ Nuevas insertadas: 8
     ✓ Duplicadas (omitidas): 0

   ══════════════════════════════════════
   ✅ TOTAL: 23 transacciones nuevas insertadas
   ```

2. **En Streamlit** (dashboard):
   - Refrescá la página
   - Vas a ver tus transacciones en el dashboard

3. **En Supabase** (verificar directamente):
   - Ir a Table Editor → transactions
   - Ver todas las transacciones insertadas

## ⚡ Automatización

### Windows (Task Scheduler)

1. Abrir **Task Scheduler**
2. Create Basic Task
3. Trigger: **Daily** a las 8:00 AM
4. Action: **Start a program**
   - Program: `C:\...\venv\Scripts\python.exe`
   - Arguments: `run.py scrape`
   - Start in: `C:\...\scraper`

### Linux/Mac (Cron)

```bash
# Editar crontab
crontab -e

# Agregar línea (ejecutar diario a las 8 AM)
0 8 * * * cd /ruta/a/scraper && /ruta/a/venv/bin/python run.py scrape
```

## 🐛 Troubleshooting

### Error: "No hay cookies"

```bash
# Exportar cookies de nuevo
python run.py export-cookies --bank bbva
python run.py export-cookies --bank galicia
```

### Error: "Connection to Supabase failed"

Verificar que `.env` tenga las credenciales correctas:
```bash
cat .env
```

### Cookies Expiradas

Las cookies expiran aprox. cada 30 días. Cuando veas errores de autenticación:
```bash
python run.py export-cookies --bank bbva
python run.py export-cookies --bank galicia
```

## 📝 Notas Importantes

### Modo DEMO Actual

🚨 **IMPORTANTE**: Los scrapers de BBVA y Galicia están en **MODO DEMO**.

Por ahora retornan **transacciones de ejemplo** para que puedas probar todo el flujo.

Para implementar el scraping REAL necesitamos:
1. Acceso a tu cuenta (cookies exportadas)
2. Inspeccionar la estructura HTML de cada sitio
3. Implementar los selectores específicos

### Próximos Pasos

1. **Exportar cookies** de ambos bancos
2. **Probar el scraper** en modo demo
3. **Ver transacciones** en el dashboard
4. **Implementar scraping real** (requiere inspeccionar sitios web)

## 🔐 Seguridad

- ✅ Las cookies se guardan en `.cookies/` (gitignored)
- ✅ Nunca se suben a GitHub
- ✅ Solo en tu máquina local
- ✅ Credenciales en `.env` (gitignored)

## ✨ Comandos Rápidos

```bash
# Ver ayuda
python run.py --help

# Exportar cookies BBVA
python run.py export-cookies --bank bbva

# Exportar cookies Galicia
python run.py export-cookies --bank galicia

# Scrapear todo
python run.py scrape

# Scrapear solo BBVA
python run.py scrape --bank bbva

# Scrapear con debug
python run.py scrape --verbose
```

---

**¿Listo para probar?**

```bash
cd scraper
python run.py scrape
```
