# 🚀 Próximos Pasos

## ✅ Lo que ya está hecho

La estructura completa del proyecto está creada con:

- 📁 15 directorios organizados
- 📄 27 archivos (Python, SQL, Markdown, Config)
- 📚 Documentación completa
- 🗄️ Schema de base de datos listo
- 🔧 Configuración inicial completa

## 🎯 Siguiente Fase: Implementación del Código

### 1️⃣ Implementar el Scraper (Prioridad Alta)

#### Archivo: `scraper/credit_card_scraper.py`
Crear la clase principal del scraper con:
- Método `scrape_all()` para scrapear todas las tarjetas
- Método `export_bbva_cookies()` para exportar cookies BBVA
- Método `export_galicia_cookies()` para exportar cookies Galicia
- Conexión a Supabase
- Manejo de errores y logging

#### Archivo: `scraper/banks/bbva.py`
Implementar scraper específico para BBVA Visa:
- Login automático (opcional)
- Navegación a sección de tarjetas
- Extracción de transacciones del último mes
- Parseo de montos, fechas y cuotas
- Return de lista de transacciones

#### Archivo: `scraper/banks/galicia.py`
Implementar scraper para Galicia (Visa + Amex):
- Similar a BBVA pero para Galicia
- Manejar ambas tarjetas (Visa y Amex)

#### Archivo: `scraper/utils.py`
Helpers para:
- Parseo de montos: `"$1.234,56"` → `1234.56`
- Parseo de fechas: `"15/12/2024"` → `"2024-12-15"`
- Detección de cuotas: `"Cuota 1 de 6"` → `"1/6"`

### 2️⃣ Implementar el Dashboard (Prioridad Alta)

#### Archivo: `dashboard/pages/1_📊_Dashboard.py`
Crear página principal con:
- KPIs principales:
  - Gasto total del mes
  - % de presupuesto usado
  - Cantidad de transacciones
  - Cuotas pendientes
- Gráficos:
  - Gastos por día (línea)
  - Gastos por tarjeta (barras)
  - Top 10 gastos (tabla)
- Tabla de transacciones recientes

#### Archivo: `dashboard/pages/2_💰_Presupuesto.py`
Crear gestión de presupuesto:
- Formulario para configurar presupuesto mensual
- Mostrar presupuesto actual
- Alertas visuales (verde/amarillo/rojo)
- Histórico de presupuestos

#### Archivo: `dashboard/pages/3_➕_Gastos_Manuales.py`
Crear formulario para gastos manuales:
- Campos: fecha, descripción, monto, categoría
- Validaciones
- Insertar en Supabase
- Mostrar gastos manuales recientes

#### Archivo: `dashboard/pages/4_⚙️_Configuración.py`
Crear página de configuración:
- Gestión de categorías (crear, editar, eliminar)
- Preferencias de usuario
- Export de datos (CSV)

### 3️⃣ Implementar Componentes Reusables

#### Archivo: `dashboard/components/kpis.py`
Funciones para mostrar métricas:
```python
def show_monthly_summary(...)
def show_budget_alert(...)
def show_credit_card_summary(...)
```

#### Archivo: `dashboard/components/charts.py`
Funciones para gráficos con Plotly:
```python
def plot_daily_expenses(...)
def plot_expenses_by_card(...)
def plot_category_distribution(...)
```

#### Archivo: `dashboard/components/tables.py`
Funciones para tablas formateadas:
```python
def show_transactions_table(...)
def show_budget_history(...)
```

### 4️⃣ Implementar Servicios

#### Archivo: `dashboard/services/budget_manager.py`
Lógica de presupuesto:
```python
def get_current_budget(...)
def calculate_budget_usage(...)
def get_budget_alert_level(...)
```

#### Archivo: `dashboard/services/analytics.py`
Queries y análisis:
```python
def get_monthly_expenses(...)
def get_expenses_by_category(...)
def get_pending_installments(...)
```

## 🧪 Testing (Opcional)

Crear tests básicos:
- `tests/test_scraper.py`
- `tests/test_dashboard.py`

## 📝 Orden Sugerido de Desarrollo

### Semana 1: Scraper MVP
1. Implementar `scraper/utils.py` (parsers)
2. Implementar `scraper/banks/bbva.py` (solo BBVA)
3. Implementar `scraper/credit_card_scraper.py`
4. Probar scraping local
5. Verificar datos en Supabase

### Semana 2: Dashboard Básico
1. Implementar `dashboard/services/analytics.py`
2. Implementar `dashboard/components/kpis.py`
3. Implementar `dashboard/pages/1_📊_Dashboard.py`
4. Deploy en Streamlit Cloud
5. Verificar login y visualización

### Semana 3: Funcionalidades Completas
1. Implementar `dashboard/pages/2_💰_Presupuesto.py`
2. Implementar `dashboard/pages/3_➕_Gastos_Manuales.py`
3. Implementar `dashboard/services/budget_manager.py`
4. Agregar validaciones y manejo de errores

### Semana 4: Polish y Galicia
1. Implementar `scraper/banks/galicia.py`
2. Implementar `dashboard/components/charts.py`
3. Implementar `dashboard/pages/4_⚙️_Configuración.py`
4. Mejorar UI/UX
5. Documentar con screenshots

## 🔧 Setup Inicial

Antes de empezar a codear:

### 1. Inicializar Git
```bash
git init
git add .
git commit -m "Initial commit: project structure"
```

### 2. Crear repo en GitHub
```bash
# Crear repo en github.com
git remote add origin https://github.com/TU_USUARIO/expense-tracker.git
git push -u origin main
```

### 3. Configurar Supabase
Seguir guía en [docs/SETUP_SUPABASE.md](docs/SETUP_SUPABASE.md)

### 4. Configurar entorno local

#### Scraper:
```bash
cd scraper
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
playwright install chromium
cp .env.example .env
# Editar .env con tus credenciales
```

#### Dashboard:
```bash
cd dashboard
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac
pip install -r requirements.txt
mkdir .streamlit
cp secrets.toml.example .streamlit/secrets.toml
# Editar secrets.toml con tus credenciales
```

## 📚 Recursos Útiles

### Playwright (Scraping)
- [Docs oficial](https://playwright.dev/python/)
- [Selectores CSS](https://developer.mozilla.org/en-US/docs/Web/CSS/CSS_Selectors)
- [DevTools para inspeccionar](https://developer.chrome.com/docs/devtools/)

### Streamlit (Dashboard)
- [Docs oficial](https://docs.streamlit.io)
- [Cheat sheet](https://docs.streamlit.io/library/cheatsheet)
- [Gallery de ejemplos](https://streamlit.io/gallery)

### Plotly (Gráficos)
- [Docs oficial](https://plotly.com/python/)
- [Ejemplos](https://plotly.com/python/plotly-express/)

### Supabase
- [Docs Python](https://supabase.com/docs/reference/python/introduction)
- [Row Level Security](https://supabase.com/docs/guides/auth/row-level-security)

## 🎯 Milestone 1: MVP Funcional

Objetivo: Tener un expense tracker funcional end-to-end

Checklist:
- [ ] Scraper funciona para al menos 1 banco (BBVA)
- [ ] Dashboard muestra transacciones del mes
- [ ] Usuario puede configurar presupuesto
- [ ] Alertas visuales funcionan
- [ ] Deploy en Streamlit Cloud activo
- [ ] README con screenshots actualizado

## 🚀 Milestone 2: Listo para Open Source

Objetivo: Proyecto listo para que otros lo usen

Checklist:
- [ ] Scrapers para 3 tarjetas funcionando
- [ ] Dashboard completo (4 páginas)
- [ ] Documentación con screenshots
- [ ] Video tutorial (opcional)
- [ ] GitHub Issues configurados
- [ ] Primera versión (v1.0.0) tagged

---

**¡Éxito con el desarrollo! 🎉**

Si tenés dudas, revisá la documentación en `docs/` o abrí un issue.
