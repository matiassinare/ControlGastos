# 🚀 Guía Rápida - Expense Tracker Personal

## ✅ Setup Completo en 3 Pasos

### 1️⃣ Configurar Base de Datos (5 min)

1. **Ya tenés Supabase** ✅
   - URL: `https://xxxxxxxxxxxxx.supabase.co`

2. **Ejecutar el schema simplificado:**
   - Ir a [SQL Editor de Supabase](https://supabase.com/dashboard/project/YOUR_PROJECT_ID/sql)
   - Copiar el contenido de `database/schema_simple.sql`
   - Pegar y ejecutar (botón **Run**)

### 2️⃣ Ejecutar Dashboard (2 min)

```bash
cd dashboard

# Si no instalaste dependencias aún:
pip install streamlit supabase plotly pandas python-dateutil

# Ejecutar app (ya configuré tus secrets)
streamlit run app.py
```

Se abrirá en `http://localhost:8501` 🎉

### 3️⃣ Usar la App

**Página Principal (Dashboard):**
- Ver gastos del mes
- Gráficos por tarjeta y por día
- Tabla de transacciones

**Agregar Gasto:**
- Agregar gastos manuales (efectivo, transferencias)

**Presupuesto:**
- Configurar límite mensual
- Ver % usado con alertas de color

## 📁 Archivos Importantes

### Archivos Nuevos (Simplificados):
- `database/schema_simple.sql` - Schema SIN autenticación ni RLS
- `dashboard/app.py` - App completa en 1 archivo
- `dashboard/services/supabase_client.py` - Actualizado (sin auth)

### Ya Configurado:
- ✅ `dashboard/.streamlit/secrets.toml` - Con tus credenciales

## 🎯 Próximos Pasos

1. **Probar que funciona:**
   ```bash
   streamlit run app.py
   ```

2. **Agregar un gasto manual** para ver que todo funciona

3. **Configurar presupuesto** del mes

4. **Luego implementamos el scraper** para BBVA y Galicia

## 🔧 Si hay Errores

### Error: ModuleNotFoundError
```bash
pip install streamlit supabase plotly pandas
```

### Error de conexión a Supabase
- Verificar que `schema_simple.sql` se ejecutó correctamente
- Verificar que `.streamlit/secrets.toml` existe

### Error: "st.secrets has no attribute 'supabase'"
```bash
# Verificar contenido:
cat .streamlit/secrets.toml

# Debe tener:
# [supabase]
# url = "https://xxxxxxxxxxxxx.supabase.co"
# key = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx"
```

## 💡 Diferencias vs Versión Anterior

| Antes | Ahora |
|-------|-------|
| Login/Registro | ❌ Eliminado |
| Multi-usuario con RLS | ❌ Eliminado |
| Múltiples páginas | ✅ Todo en 1 app |
| GitHub necesario | ❌ No necesario |
| Deploy en Streamlit Cloud | ⏸️ Opcional (después) |

## ✨ Beneficios

- ⚡ Más rápido de configurar
- 🎯 Código más simple
- 💻 Todo corre local
- 🔒 Seguro (solo vos tenés acceso)
- 🚀 Listo para usar YA

---

**¿Listo? Ejecutá:**
```bash
cd dashboard
streamlit run app.py
```
