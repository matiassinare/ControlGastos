# 🔧 Configuración de Supabase

## ⚠️ IMPORTANTE: Actualizar Credenciales

Actualmente, la API key de Supabase en tu configuración parece estar incompleta.

## 📋 Pasos para obtener las credenciales correctas:

### 1. Ve a tu proyecto en Supabase
   - https://supabase.com/dashboard/project/YOUR_PROJECT_ID

### 2. Navega a "Project Settings" (⚙️ en el menú izquierdo)

### 3. Click en "API" en el menú lateral

### 4. Copia las credenciales:
   - **Project URL**: `https://xxxxxxxxxxxxx.supabase.co`
   - **anon public key**: Será una key MUY LARGA que empieza con `eyJ...`

### 5. Actualiza el archivo `.streamlit/secrets.toml`

Reemplaza el contenido con:

```toml
[supabase]
url = "https://xxxxxxxxxxxxx.supabase.co"
key = "TU_ANON_KEY_COMPLETA_AQUI"  # <-- Debe ser MUY larga (200+ caracteres)
```

### 6. Ejecutar migración SQL

Ve a Supabase → **SQL Editor** y ejecuta el contenido del archivo:

📄 `database/migration_add_statement_period.sql`

Esto agregará las columnas necesarias:
- `statement_period` - Para organizar gastos por mes de resumen
- `installments` - Para manejar cuotas

### 7. Reinicia Streamlit

Después de actualizar, reinicia el servidor de Streamlit para que cargue las nuevas credenciales.

---

## ✅ Verificación

Una vez actualizado, cuando visites http://localhost:8502 deberías ver:
- Los datos persisten al refrescar la página
- Puedes importar PDFs y las transacciones se guardan
- Las cuotas se propagan automáticamente a meses futuros
- Todo se guarda en Supabase (no se pierde al cerrar el navegador)

---

## 🔒 Seguridad

**NUNCA** subas el archivo `.streamlit/secrets.toml` a GitHub.
Ya está agregado al `.gitignore` para proteger tus credenciales.
