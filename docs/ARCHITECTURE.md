# 🏗️ Arquitectura del Sistema

## Diagrama General

```
┌─────────────────────────────────────────────────────────────────┐
│                         USUARIO                                 │
│  ┌──────────────┐              ┌──────────────┐                │
│  │   Scraper    │              │  Dashboard   │                │
│  │   (Local)    │              │  (Browser)   │                │
│  └──────┬───────┘              └──────┬───────┘                │
└─────────┼──────────────────────────────┼──────────────────────┘
          │                              │
          │ HTTPS                        │ HTTPS
          │                              │
          ▼                              ▼
┌─────────────────────────────────────────────────────────────────┐
│                      SUPABASE (CLOUD)                           │
│  ┌─────────────┐   ┌─────────────┐   ┌─────────────┐          │
│  │ PostgreSQL  │   │    Auth     │   │  Storage    │          │
│  │  Database   │   │  (JWT)      │   │  (Futuro)   │          │
│  └─────────────┘   └─────────────┘   └─────────────┘          │
│                                                                 │
│  Row Level Security (RLS) - Aislamiento por usuario            │
└─────────────────────────────────────────────────────────────────┘
```

## Componentes

### 1. Scraper (Local)

**Responsabilidad**: Extraer transacciones de los sitios bancarios y guardarlas en Supabase.

**Tecnologías**:
- Python 3.10+
- Playwright (navegador headless)
- python-dotenv (variables de entorno)
- supabase-py (cliente de base de datos)

**Flujo**:
1. Usuario ejecuta `python run.py scrape`
2. Carga cookies guardadas (sesión persistente)
3. Navega a cada sitio bancario con Playwright
4. Extrae transacciones del último mes
5. Parsea montos, fechas y cuotas
6. Inserta en Supabase con `upsert` (evita duplicados)

**Frecuencia**: Manual o automático (cron local/GitHub Actions)

**Archivos**:
```
scraper/
├── run.py                 # Entry point
├── credit_card_scraper.py # Clase principal
├── banks/
│   ├── bbva.py           # Lógica específica BBVA
│   └── galicia.py        # Lógica específica Galicia
└── utils.py              # Parseo de montos/fechas
```

### 2. Dashboard (Streamlit Cloud)

**Responsabilidad**: Visualizar gastos, gestionar presupuesto y agregar transacciones manuales.

**Tecnologías**:
- Streamlit (framework web)
- Plotly (gráficos interactivos)
- Pandas (procesamiento de datos)
- supabase-py (cliente de base de datos)

**Flujo**:
1. Usuario accede a `https://your-app.streamlit.app`
2. Login con Supabase Auth
3. Dashboard carga datos del usuario (RLS automático)
4. Muestra KPIs, gráficos y tablas
5. Permite agregar gastos manuales

**Páginas**:
- `📊 Dashboard`: KPIs y gráficos principales
- `💰 Presupuesto`: Configurar límite mensual
- `➕ Gastos Manuales`: Agregar transacciones
- `⚙️ Configuración`: Categorías y preferencias

**Archivos**:
```
dashboard/
├── streamlit_app.py       # Entry point (login)
├── pages/
│   ├── 1_📊_Dashboard.py
│   ├── 2_💰_Presupuesto.py
│   ├── 3_➕_Gastos_Manuales.py
│   └── 4_⚙️_Configuración.py
├── components/            # UI reusables
└── services/              # Lógica de negocio
```

### 3. Supabase (Cloud)

**Responsabilidad**: Base de datos, autenticación y seguridad.

**Servicios**:
- **PostgreSQL**: Almacenamiento de datos
- **Auth**: Manejo de usuarios (email/password)
- **Row Level Security**: Aislamiento de datos por usuario
- **Real-time** (futuro): Sincronización en tiempo real

**Tablas**:
- `transactions`: Transacciones de tarjetas
- `budget`: Presupuesto mensual
- `categories`: Categorías personalizadas

**Seguridad**:
```sql
-- Ejemplo de RLS
CREATE POLICY "Users see only their transactions"
ON transactions FOR ALL
USING (auth.uid() = user_id);
```

Cada usuario solo puede ver/modificar sus propios datos.

## Flujo de Datos

### Scraping → Supabase

```
[Banco Web] → [Playwright] → [Parser] → [Supabase Upsert]
                                             ↓
                                    [PostgreSQL (RLS)]
```

### Dashboard → Usuario

```
[PostgreSQL (RLS)] → [Supabase Client] → [Streamlit] → [Plotly Charts]
                                             ↓
                                        [User Browser]
```

## Autenticación

### Scraper
- **No requiere login**: usa `anon` key de Supabase
- **RLS**: inserts automáticamente asociados al usuario autenticado

### Dashboard
- **Supabase Auth**: login con email/password
- **JWT Token**: almacenado en `st.session_state`
- **RLS**: queries automáticamente filtradas por `user_id`

## Escalabilidad

### Tier Free Actual
- **Supabase**: 500 MB storage, 2 GB bandwidth/mes
- **Streamlit Cloud**: 1 app, recursos compartidos
- **Playwright**: corre local (sin límites)

### Futuro (si crece)
- **Supabase Pro**: $25/mes (8 GB storage)
- **Streamlit Cloud Pro**: $200/mes (recursos dedicados)
- **Scraper Cloud**: Railway/Render con cron jobs

## Seguridad

### Datos Sensibles
- **Cookies**: almacenadas localmente (`.gitignore`)
- **Credenciales**: en `.env` (`.gitignore`)
- **Secrets Streamlit**: cifrados en Streamlit Cloud
- **Supabase Keys**: nunca en código, solo en `.env`

### Base de Datos
- **RLS**: aislamiento por usuario
- **HTTPS**: todas las conexiones encriptadas
- **JWT**: tokens con expiración

### Scraper
- **Headless browser**: no GUI, más seguro
- **User-Agent real**: evita detección
- **Rate limiting**: delays entre requests

## Trade-offs de Diseño

### ¿Por qué scraper local?
- **Pros**:
  - Gratis (no hosting)
  - Cookies en tu máquina (más seguro)
  - Control total del timing
- **Contras**:
  - Requiere ejecutar manualmente
  - No automático (salvo cron local)

### ¿Por qué Supabase?
- **Pros**:
  - Tier free generoso
  - RLS built-in
  - Auth incluida
  - Real-time fácil
- **Contras**:
  - Vendor lock-in
  - Límites en free tier

### ¿Por qué Streamlit?
- **Pros**:
  - Deploy en 1 clic
  - Python puro (no JS)
  - UI rápida de construir
- **Contras**:
  - Limitado en customización
  - Recursos compartidos (free tier)

## Próximos Pasos

1. **GitHub Actions**: scraper automático (cron diario)
2. **Notificaciones**: email cuando te pasas del presupuesto
3. **Categorización ML**: auto-clasificar gastos
4. **Export PDF**: reportes mensuales
5. **Multi-moneda**: soporte USD/EUR
