# 📝 Resumen del Estado Actual del Proyecto

## 📅 Estado al: 16 de Diciembre 2025

Este documento resume el estado actual del **Expense Tracker**, los cambios realizados recientemente y las tareas pendientes.

---

## 🚀 Lo que FUNCIONA (Implementado)

### 📊 Dashboard (Streamlit)
1.  **Estructura Principal**:
    *   `streamlit_app.py` funcionando como punto de entrada.
    *   Menú lateral con navegación funcional.
    *   Detección automática de conexión a base de datos (Supabase) o modo Local (Mock).

2.  **Páginas Implementadas**:
    *   **`1_📊_Resumen`**: Visualización de gastos (Gráficos y métricas).
    *   **`2_📤_Importar`**: Módulo **NUEVO** para subir resúmenes de tarjeta en PDF.
        *   Procesa el texto del PDF.
        *   Detecta patrón de fechas y montos.
        *   Permite guardar las transacciones extraídas en la sesión actual (Modo Mock) o BD.

3.  **Servicios de Datos (`data_service.py`)**:
    *   **Modo Híbrido**: El sistema funciona aunque no haya base de datos conectada.
    *   **Persistencia Temporal**: Si estás en modo Mock, los datos importados del PDF se guardan en la memoria de la sesión (`st.session_state`) para que puedas verlos en el Resumen sin necesitar base de datos real.

### 🤖 Scraper (Python)
1.  **Infraestructura**:
    *   `run.py`: CLI para ejecutar comandos (`python run.py scrape`).
    *   `credit_card_scraper.py`: Orquestador principal.
2.  **Bancos**:
    *   **Galicia**: Lógica implementada para Visa y Amex.
    *   **BBVA**: Estructura lista, pero lógica pendiente.

---

## 🚧 Lo que FALTA (Pendiente / En Desarrollo)

### Dashboard
*   [ ] **Página de Presupuesto**: Link deshabilitado actualmente. Falta implementar lógica y UI para setear límites mensuales.
*   [ ] **Carga Manual Individual**: No hay formulario para cargar "Compré un café - $500" manualmente (solo vía importación masiva PDF o Scraper).
*   [ ] **Categorización Inteligente**: Las transacciones importadas no tienen categoría asignada automáticamente.
*   [ ] **Configuración**: Página de ajustes (para editar categorías, targets de presupuesto) no creada.

### Scraper
*   [ ] **Implementación BBVA**: El método `scrape_bbva` está vacío (TODO).
*   [ ] **Manejo de Cookies**: Se marcó como "deprecated" la exportación manual a favor de login con credenciales, pero hay que validar que `GaliciaScraper` maneje el login 100% automático.

---

## 📂 Cambios Recientes (Resumen Técnico)

1.  **Creado `dashboard/pages/2_📤_Importar.py`**:
    *   Se agregó librería `pdfplumber` (verificar `requirements.txt`).
    *   Lógica de parsing de texto crudo a DataFrame.
    *   Integración con `DataService` para inyectar datos en el flujo de la app.

2.  **Modificado `dashboard/services/data_service.py`**:
    *   Ahora soporta `add_manual_transaction`.
    *   Maneja duplicados básicos (misma fecha, descripción y monto).
    *   Inicializa `mock_transactions` vacío (count=0) para no ensuciar la vista con datos falsos si el usuario quiere ver sus propios datos importados.

3.  **Ajustes en `dashboard/streamlit_app.py`**:
    *   Se ocultaron links a páginas no terminadas para limpiar la UI.

---

## 🎯 Próximos Pasos Recomendados

1.  **Validar Importación Real**: Probar el importador de PDF con un resumen real de tarjeta (tapando datos sensibles) para calibrar el parser regex.
2.  **Activar Carga Manual**: Habilitar un formulario simple en `3_➕_Gastos_Manuales` para gastos efectivo/diarios.
3.  **Persistencia Local**: Actualmente si refrescas la página en modo Mock, se borran los datos importados. Evaluar guardar en un CSV local o JSON si no se quiere usar Supabase todavía.
