# 🗄️ Setup de Supabase

Guía paso a paso para configurar tu base de datos PostgreSQL en Supabase (100% gratuito).

## ⏱️ Tiempo estimado: 5 minutos

## 📋 Requisitos

- Cuenta de email válida
- Navegador web

## 🚀 Pasos

### 1. Crear Cuenta en Supabase

1. Ir a [supabase.com](https://supabase.com)
2. Hacer clic en **Start your project**
3. Elegir método de autenticación:
   - **GitHub** (recomendado)
   - **Email/Password**

![Supabase Login](../assets/screenshots/supabase-login.png)

### 2. Crear Nuevo Proyecto

1. Hacer clic en **New Project**
2. Completar formulario:
   - **Organization**: Crear nueva o usar existente
   - **Project Name**: `expense-tracker` (o tu nombre preferido)
   - **Database Password**: Generar automáticamente (guardar en lugar seguro)
   - **Region**: `South America (São Paulo)` (más cercano a Argentina)
   - **Pricing Plan**: **Free** (seleccionar)

3. Hacer clic en **Create new project**

![Supabase New Project](../assets/screenshots/supabase-new-project.png)

**⏳ Esperar 2-3 minutos** mientras Supabase provisiona tu base de datos.

### 3. Ejecutar Schema SQL

1. En el panel izquierdo, ir a **SQL Editor**
2. Hacer clic en **New Query**
3. Copiar todo el contenido de `database/schema.sql` de este repositorio
4. Pegar en el editor
5. Hacer clic en **Run** (o `Ctrl+Enter`)

![Supabase SQL Editor](../assets/screenshots/supabase-sql-editor.png)

**✅ Verificar**: Deberías ver el mensaje "Success. No rows returned"

### 4. Verificar Tablas Creadas

1. En el panel izquierdo, ir a **Table Editor**
2. Deberías ver 3 tablas:
   - `transactions`
   - `budget`
   - `categories`

![Supabase Tables](../assets/screenshots/supabase-tables.png)

### 5. Obtener Credenciales

1. En el panel izquierdo, ir a **Settings** → **API**
2. Copiar las siguientes credenciales:

   - **Project URL**:
     ```
     https://xxxxxxxxxxxxx.supabase.co
     ```

   - **anon public**:
     ```
     eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.xxxxxxxxxxxxx...
     ```

![Supabase API Credentials](../assets/screenshots/supabase-api.png)

**⚠️ IMPORTANTE**:
- Guardar estas credenciales en un lugar seguro
- **NO compartir** públicamente
- La clave `anon` es segura para usar en frontend (tiene RLS)

### 6. Configurar Autenticación (Opcional)

Si quieres que otros usuarios puedan registrarse:

1. Ir a **Authentication** → **Providers**
2. Habilitar **Email**
3. Configurar:
   - **Enable Email Signup**: ON
   - **Confirm Email**: OFF (para testing) o ON (para producción)

![Supabase Auth](../assets/screenshots/supabase-auth.png)

### 7. (Opcional) Cargar Datos de Ejemplo

Para probar el dashboard con datos de ejemplo:

1. Ir a **SQL Editor**
2. Copiar contenido de `database/seed.sql`
3. Pegar y ejecutar

**⚠️ NOTA**: Esto creará transacciones de ejemplo. Puedes eliminarlas después.

## 📝 Próximos Pasos

Ahora que tienes Supabase configurado, necesitas:

1. **Configurar Dashboard**: [SETUP_STREAMLIT.md](SETUP_STREAMLIT.md)
2. **Configurar Scraper**: [SETUP_SCRAPER.md](SETUP_SCRAPER.md)

## 🔐 Seguridad

### Row Level Security (RLS)

El schema incluye políticas de seguridad que garantizan:
- Cada usuario solo ve **sus propios datos**
- No puede acceder a datos de otros usuarios
- Funciona automáticamente con Supabase Auth

Verificar RLS:
1. Ir a **Authentication** → **Policies**
2. Deberías ver políticas para cada tabla

### Backup

Supabase hace backups automáticos, pero recomendamos:

```bash
# Exportar schema
pg_dump -h db.xxxxx.supabase.co -U postgres -s expense_tracker > backup_schema.sql

# Exportar datos
pg_dump -h db.xxxxx.supabase.co -U postgres -a expense_tracker > backup_data.sql
```

## 🐛 Troubleshooting

### Error: "relation already exists"

**Causa**: Intentaste ejecutar `schema.sql` dos veces.

**Solución**:
1. Ir a **Table Editor**
2. Eliminar tablas existentes
3. Ejecutar `schema.sql` de nuevo

### Error: "permission denied for schema public"

**Causa**: Permisos incorrectos.

**Solución**:
```sql
GRANT ALL ON SCHEMA public TO postgres, anon, authenticated;
```

### No puedo ver datos en Table Editor

**Causa**: RLS está activado y no estás autenticado.

**Solución**:
1. Ir a **SQL Editor**
2. Ejecutar query directamente (bypasea RLS)
```sql
SELECT * FROM transactions;
```

## 📚 Recursos

- [Documentación Supabase](https://supabase.com/docs)
- [PostgreSQL Tutorial](https://www.postgresql.org/docs/current/tutorial.html)
- [Row Level Security Guide](https://supabase.com/docs/guides/auth/row-level-security)

## ✅ Checklist

- [ ] Cuenta de Supabase creada
- [ ] Proyecto creado (región São Paulo)
- [ ] Schema ejecutado sin errores
- [ ] 3 tablas visibles en Table Editor
- [ ] Project URL copiada
- [ ] anon key copiada
- [ ] (Opcional) Email auth habilitado
- [ ] (Opcional) Datos de ejemplo cargados

## 🎉 Siguiente paso

Continuar con [SETUP_STREAMLIT.md](SETUP_STREAMLIT.md) para deployar el dashboard.
