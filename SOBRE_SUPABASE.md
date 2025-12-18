# ¿Para qué estás usando Supabase?

## Actualmente

Supabase te está proporcionando:

1. **Base de datos PostgreSQL en la nube** - Para guardar tus transacciones de forma persistente
2. **API REST automática** - No necesitas escribir endpoints, Supabase los genera automáticamente
3. **Sincronización entre dispositivos** - Si accedes desde otra computadora, ves los mismos datos
4. **Backup automático** - Tus datos están en la nube, no solo en tu máquina local

## Arquitectura Actual

```
Dashboard Streamlit (Frontend)
         ↓
   Supabase Client
         ↓
Supabase Cloud (Backend)
         ↓
PostgreSQL Database
```

## ¿Es necesario Supabase?

**NO es estrictamente necesario**. Podrías usar alternativas más simples:

### Opción A: SQLite Local (Sin Internet)
- Base de datos en un archivo `.db` en tu computadora
- Más simple, sin necesidad de configuración
- **Ventaja**: No necesitas internet ni credenciales
- **Desventaja**: Solo accesible desde tu computadora, sin backup automático

### Opción B: CSV/Excel (Ultra Simple)
- Guardar transacciones en archivos CSV o Excel
- **Ventaja**: Súper simple, puedes abrir con Excel
- **Desventaja**: No hay consultas SQL, más limitado

### Opción C: Mantener Supabase (Actual)
- **Ventaja**: Datos en la nube, acceso desde cualquier lugar, backup automático
- **Desventaja**: Necesitas configurar credenciales y mantener cuenta de Supabase

## Recomendación

Si estás usando esto **solo vos, desde una sola computadora**, Supabase puede ser overkill.

**Te sugiero cambiar a SQLite local** porque:
- Es más simple (no necesitas .env con credenciales)
- Funciona sin internet
- Sigue siendo una base de datos SQL profesional
- Es lo que usan la mayoría de apps locales (como tu navegador Chrome)

¿Querés que cambie a SQLite o preferís mantener Supabase?
