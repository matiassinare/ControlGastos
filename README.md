# 💰 Expense Tracker Argentina

Aplicación open-source para trackear gastos de tarjetas de crédito argentinas y presupuesto mensual.

## 🚀 Características

- **Scraping automático** de 3 tarjetas: Visa BBVA, Visa Galicia, Amex Galicia
- **Dashboard interactivo** con métricas en tiempo real
- **Gestión de presupuesto** mensual con alertas visuales
- **Gastos manuales** para efectivo y transferencias
- **100% gratuito**: usa tier free de Supabase y Streamlit Cloud
- **Deploy en 15 minutos**: fork, configurar y usar

## 📊 Stack Tecnológico

- **Backend**: Supabase (PostgreSQL + Auth)
- **Frontend**: Streamlit Cloud
- **Scraper**: Python + Playwright (local)
- **Visualización**: Plotly

## 🎯 Demo

[🔗 Ver demo en vivo](https://your-app.streamlit.app) *(próximamente)*

## 📸 Screenshots

*(Agregar screenshots del dashboard aquí)*

## 🏗️ Arquitectura

```
┌─────────────┐     ┌──────────────┐     ┌─────────────┐
│   Scraper   │────▶│  Supabase    │◀────│  Dashboard  │
│   (Local)   │     │ (PostgreSQL) │     │ (Streamlit) │
└─────────────┘     └──────────────┘     └─────────────┘
     Python              Cloud                 Cloud
```

Ver [ARCHITECTURE.md](docs/ARCHITECTURE.md) para más detalles.

## 🚦 Setup Rápido (15 minutos)

### 1️⃣ Crear Proyecto Supabase (5 min)

1. Ir a [supabase.com](https://supabase.com) y crear cuenta
2. Crear nuevo proyecto
3. En SQL Editor, ejecutar `database/schema.sql`
4. Copiar **Project URL** y **anon key** desde Settings → API

Ver guía completa: [SETUP_SUPABASE.md](docs/SETUP_SUPABASE.md)

### 2️⃣ Deploy Dashboard (3 min)

1. Hacer fork de este repositorio
2. Ir a [share.streamlit.io](https://share.streamlit.io)
3. Conectar GitHub y seleccionar tu fork
4. En **Secrets**, agregar:
   ```toml
   [supabase]
   url = "TU_SUPABASE_URL"
   key = "TU_SUPABASE_KEY"
   ```
5. Hacer clic en Deploy

Ver guía completa: [SETUP_STREAMLIT.md](docs/SETUP_STREAMLIT.md)

### 3️⃣ Configurar Scraper Local (7 min)

```bash
# Clonar tu fork
git clone https://github.com/TU_USUARIO/expense-tracker.git
cd expense-tracker/scraper

# Instalar dependencias
pip install -r requirements.txt
playwright install chromium

# Configurar variables de entorno
cp .env.example .env
# Editar .env con tus credenciales de Supabase

# Exportar cookies de los bancos
python run.py export-cookies

# Ejecutar scraper
python run.py scrape
```

Ver guía completa: [SETUP_SCRAPER.md](docs/SETUP_SCRAPER.md)

## 📖 Documentación

- [ARCHITECTURE.md](docs/ARCHITECTURE.md) - Arquitectura del sistema
- [SETUP_SUPABASE.md](docs/SETUP_SUPABASE.md) - Configuración de base de datos
- [SETUP_STREAMLIT.md](docs/SETUP_STREAMLIT.md) - Deploy del dashboard
- [SETUP_SCRAPER.md](docs/SETUP_SCRAPER.md) - Configuración del scraper

## 🗂️ Estructura del Proyecto

```
expense-tracker/
├── database/           # Schemas SQL
├── scraper/           # Scraper de tarjetas (local)
├── dashboard/         # Dashboard Streamlit (cloud)
├── docs/             # Documentación
└── .github/          # Workflows y templates
```

## 🛠️ Comandos del Scraper

```bash
# Exportar cookies de los bancos
python run.py export-cookies

# Scrapear todas las tarjetas
python run.py scrape

# Scrapear banco específico
python run.py scrape --bank bbva
python run.py scrape --bank galicia

# Ver ayuda
python run.py --help
```

## 🔐 Seguridad

- **Row Level Security (RLS)**: cada usuario ve solo sus datos
- **Cookies locales**: nunca se suben al repositorio
- **Credenciales**: almacenadas en `.env` (gitignored)
- **Secrets**: manejados por Supabase y Streamlit Cloud

## 🤝 Contribuciones

Las contribuciones son bienvenidas! Por favor:

1. Fork el proyecto
2. Crear branch para tu feature (`git checkout -b feature/AmazingFeature`)
3. Commit tus cambios (`git commit -m 'Add: amazing feature'`)
4. Push al branch (`git push origin feature/AmazingFeature`)
5. Abrir Pull Request

Ver [CONTRIBUTING.md](CONTRIBUTING.md) para más detalles.

## 📋 Roadmap

- [x] Schema de base de datos
- [x] Scraper básico BBVA
- [ ] Scraper Galicia (Visa y Amex)
- [ ] Dashboard con KPIs
- [ ] Gestión de presupuesto
- [ ] Gastos manuales
- [ ] Categorización automática
- [ ] Exportar a CSV/PDF
- [ ] GitHub Actions (scraper automático)
- [ ] Notificaciones (email/Telegram)

## 🐛 Reportar Bugs

Abrir un issue en [GitHub Issues](https://github.com/TU_USUARIO/expense-tracker/issues)

## 📄 Licencia

MIT License - ver [LICENSE](LICENSE) para más detalles.

## ⭐ Soporte

Si este proyecto te fue útil, dejá una estrella ⭐ en GitHub!

---

**Hecho con ❤️ en Argentina**
