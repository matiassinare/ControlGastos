"""
Expense Tracker - Dashboard Principal

Aplicación Streamlit para visualizar gastos de tarjetas de crédito.
"""

import streamlit as st
from services.supabase_client import get_supabase_client

# Configuración de la página
st.set_page_config(
    page_title="Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado mejorado
st.markdown("""
    <style>
    /* Importar fuente moderna */
    @import url('https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap');

    /* Variables de colores - Tema Claro */
    :root {
        --primary-color: #6366f1;
        --secondary-color: #8b5cf6;
        --success-color: #10b981;
        --danger-color: #ef4444;
        --warning-color: #f59e0b;
        --background-light: #f8fafc;
        --background-white: #ffffff;
        --card-bg: #ffffff;
        --text-primary: #1e293b;
        --text-secondary: #64748b;
        --border-color: #e2e8f0;
        --shadow-sm: 0 1px 3px rgba(0, 0, 0, 0.1);
        --shadow-md: 0 4px 6px rgba(0, 0, 0, 0.1);
        --shadow-lg: 0 10px 15px rgba(0, 0, 0, 0.1);
    }

    /* Fuente global */
    html, body, [class*="css"] {
        font-family: 'Inter', -apple-system, BlinkMacSystemFont, sans-serif;
    }

    /* Header principal mejorado */
    .main-header {
        font-size: 3rem;
        font-weight: 700;
        background: linear-gradient(135deg, var(--primary-color) 0%, var(--secondary-color) 100%);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        background-clip: text;
        margin-bottom: 1rem;
        animation: fadeIn 0.6s ease-in;
    }

    @keyframes fadeIn {
        from { opacity: 0; transform: translateY(-10px); }
        to { opacity: 1; transform: translateY(0); }
    }

    /* Cards mejorados - Tema Claro */
    .custom-card {
        background: var(--card-bg);
        border-radius: 16px;
        padding: 1.5rem;
        box-shadow: var(--shadow-md);
        border: 1px solid var(--border-color);
        transition: all 0.3s ease;
        margin-bottom: 1rem;
    }

    .custom-card:hover {
        transform: translateY(-2px);
        box-shadow: var(--shadow-lg);
        border-color: var(--primary-color);
    }

    /* Badges de estado */
    .status-badge {
        display: inline-block;
        padding: 0.25rem 0.75rem;
        border-radius: 9999px;
        font-size: 0.875rem;
        font-weight: 500;
        margin-top: 0.5rem;
    }

    .badge-success {
        background-color: rgba(16, 185, 129, 0.2);
        color: var(--success-color);
    }

    .badge-warning {
        background-color: rgba(245, 158, 11, 0.2);
        color: var(--warning-color);
    }

    .badge-info {
        background-color: rgba(99, 102, 241, 0.2);
        color: var(--primary-color);
    }

    /* Sidebar mejorado - Tema Claro */
    [data-testid="stSidebar"] {
        background: linear-gradient(180deg, #ffffff 0%, #f8fafc 100%);
        border-right: 1px solid var(--border-color);
    }

    [data-testid="stSidebar"] [data-testid="stMarkdownContainer"] {
        color: var(--text-primary);
    }

    [data-testid="stSidebar"] h1, [data-testid="stSidebar"] h3 {
        color: var(--text-primary);
    }

    /* Botones mejorados */
    .stButton > button {
        border-radius: 8px;
        font-weight: 500;
        transition: all 0.2s ease;
        border: none;
    }

    .stButton > button:hover {
        transform: translateY(-1px);
        box-shadow: 0 4px 12px rgba(99, 102, 241, 0.4);
    }

    /* Links del sidebar */
    [data-testid="stSidebar"] a {
        text-decoration: none;
        transition: all 0.2s ease;
    }

    [data-testid="stSidebar"] a:hover {
        transform: translateX(4px);
    }

    /* Ocultar elementos de Streamlit */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}

    /* Métricas mejoradas */
    [data-testid="stMetricValue"] {
        font-size: 2rem;
        font-weight: 700;
    }

    /* Animación de entrada */
    .element-container {
        animation: slideIn 0.4s ease-out;
    }

    @keyframes slideIn {
        from {
            opacity: 0;
            transform: translateY(10px);
        }
        to {
            opacity: 1;
            transform: translateY(0);
        }
    }
    </style>
""", unsafe_allow_html=True)


def show_welcome_card():
    """Mostrar card de bienvenida moderna."""
    st.markdown("""
        <div class="custom-card">
            <h2 style="margin-top: 0; color: var(--text-primary);">🚀 Bienvenido a Expense Tracker</h2>
            <p style="color: var(--text-secondary); font-size: 1.1rem;">
                Tu asistente personal para gestionar gastos de tarjetas de crédito
            </p>
            <br>
            <div style="display: grid; grid-template-columns: repeat(auto-fit, minmax(250px, 1fr)); gap: 1rem;">
                <div style="padding: 1rem; background: rgba(99, 102, 241, 0.08); border-radius: 12px; border: 1px solid rgba(99, 102, 241, 0.2);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📊</div>
                    <h3 style="margin: 0.5rem 0; color: var(--text-primary);">Visualización</h3>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">
                        Gráficos y métricas de tus gastos en tiempo real
                    </p>
                </div>
                <div style="padding: 1rem; background: rgba(139, 92, 246, 0.08); border-radius: 12px; border: 1px solid rgba(139, 92, 246, 0.2);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">📤</div>
                    <h3 style="margin: 0.5rem 0; color: var(--text-primary);">Importación</h3>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">
                        Sube tus resúmenes de tarjeta en PDF automáticamente
                    </p>
                </div>
                <div style="padding: 1rem; background: rgba(16, 185, 129, 0.08); border-radius: 12px; border: 1px solid rgba(16, 185, 129, 0.2);">
                    <div style="font-size: 2rem; margin-bottom: 0.5rem;">🔄</div>
                    <h3 style="margin: 0.5rem 0; color: var(--text-primary);">Sincronización</h3>
                    <p style="color: var(--text-secondary); font-size: 0.9rem;">
                        Conectado con Supabase para persistencia de datos
                    </p>
                </div>
            </div>
        </div>
    """, unsafe_allow_html=True)


def show_quick_actions():
    """Mostrar acciones rápidas."""
    st.markdown("### ⚡ Acciones Rápidas")

    col1, col2, col3 = st.columns(3)

    with col1:
        if st.button("📊 Ver Resumen", use_container_width=True, type="primary"):
            st.switch_page("pages/1_📊_Resumen.py")

    with col2:
        if st.button("📤 Importar PDF", use_container_width=True):
            st.switch_page("pages/2_📤_Importar.py")

    with col3:
        st.button("⚙️ Configuración", use_container_width=True, disabled=True)


def show_connection_status():
    """Mostrar estado de conexión de forma visual."""
    try:
        supabase = get_supabase_client()
        if supabase:
            st.markdown("""
                <div class="custom-card">
                    <h3 style="margin-top: 0; color: var(--text-primary);">🔌 Estado de Conexión</h3>
                    <span class="status-badge badge-success">✅ Conectado a Supabase</span>
                    <p style="color: var(--text-secondary); margin-top: 1rem; font-size: 0.9rem;">
                        Tus datos se sincronizan automáticamente con la nube
                    </p>
                </div>
            """, unsafe_allow_html=True)
        else:
            if st.session_state.get('use_mock_data', True):
                st.markdown("""
                    <div class="custom-card">
                        <h3 style="margin-top: 0; color: var(--text-primary);">🔌 Estado de Conexión</h3>
                        <span class="status-badge badge-info">ℹ️ Modo Demo</span>
                        <p style="color: var(--text-secondary); margin-top: 1rem; font-size: 0.9rem;">
                            Usando datos de prueba locales
                        </p>
                    </div>
                """, unsafe_allow_html=True)
            else:
                st.markdown("""
                    <div class="custom-card">
                        <h3 style="margin-top: 0; color: var(--text-primary);">🔌 Estado de Conexión</h3>
                        <span class="status-badge badge-warning">⚠️ Sin configurar</span>
                        <p style="color: var(--text-secondary); margin-top: 1rem; font-size: 0.9rem;">
                            Configura Supabase en el archivo .env
                        </p>
                    </div>
                """, unsafe_allow_html=True)
    except Exception:
        st.markdown("""
            <div class="custom-card">
                <h3 style="margin-top: 0; color: var(--text-primary);">🔌 Estado de Conexión</h3>
                <span class="status-badge badge-warning">⚠️ Modo Local</span>
                <p style="color: var(--text-secondary); margin-top: 1rem; font-size: 0.9rem;">
                    Trabajando sin conexión a la base de datos
                </p>
            </div>
        """, unsafe_allow_html=True)


def show_main_app():
    """Mostrar aplicación principal."""
    # Sidebar mejorado
    with st.sidebar:
        st.markdown('<h1 style="text-align: center; margin-bottom: 2rem;">💰 Expense<br>Tracker</h1>',
                   unsafe_allow_html=True)

        st.markdown("---")

        # Navegación mejorada
        st.markdown("### 📱 Navegación")
        st.page_link("pages/1_📊_Resumen.py", label="📊 Resumen", use_container_width=True)
        st.page_link("pages/2_📤_Importar.py", label="📤 Importar PDF", use_container_width=True)

        st.markdown("---")

        # Info
        st.markdown("### ℹ️ Info")
        st.markdown("""
            <div style="font-size: 0.9rem; color: var(--text-secondary);">
                <p><strong>Versión:</strong> 1.0.0</p>
                <p><strong>Modo:</strong> Personal</p>
            </div>
        """, unsafe_allow_html=True)

    # Contenido principal
    st.markdown('<p class="main-header">💰 Expense Tracker</p>', unsafe_allow_html=True)

    # Welcome card
    show_welcome_card()

    st.markdown("<br>", unsafe_allow_html=True)

    # Quick actions
    show_quick_actions()

    st.markdown("<br>", unsafe_allow_html=True)

    # Connection status
    show_connection_status()


def main():
    """Función principal."""
    show_main_app()


if __name__ == '__main__':
    main()
