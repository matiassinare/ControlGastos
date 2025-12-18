"""
Expense Tracker - Dashboard Personal
Dashboard simplificado sin autenticación
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
from services.supabase_client import get_supabase_client

# Configuración de página
st.set_page_config(
    page_title="💰 Expense Tracker",
    page_icon="💰",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personalizado
st.markdown("""
    <style>
    .main-header {
        font-size: 2.5rem;
        font-weight: bold;
        color: #FF4B4B;
        margin-bottom: 1rem;
    }
    .metric-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin: 0.5rem 0;
    }
    </style>
""", unsafe_allow_html=True)

# Cliente Supabase
supabase = get_supabase_client()


def get_current_month_expenses():
    """Obtener gastos del mes actual."""
    today = datetime.now()
    first_day = today.replace(day=1).strftime('%Y-%m-%d')

    response = supabase.table('transactions')\
        .select('*')\
        .gte('date', first_day)\
        .order('date', desc=True)\
        .execute()

    if response.data:
        return pd.DataFrame(response.data)
    return pd.DataFrame()


def get_budget_for_month(year_month):
    """Obtener presupuesto del mes."""
    response = supabase.table('budget')\
        .select('*')\
        .eq('year_month', year_month)\
        .execute()

    if response.data and len(response.data) > 0:
        return response.data[0]
    return None


def show_kpis(df, budget):
    """Mostrar métricas principales."""
    col1, col2, col3, col4 = st.columns(4)

    # Total gastado
    total_spent = df['amount'].sum() if not df.empty else 0

    with col1:
        st.metric("💳 Gasto Total", f"${total_spent:,.2f}")

    # Presupuesto usado
    if budget:
        budget_limit = budget['budget_limit']
        percentage = (total_spent / budget_limit * 100) if budget_limit > 0 else 0

        # Color según porcentaje
        if percentage < 70:
            emoji = "🟢"
        elif percentage < 90:
            emoji = "🟡"
        else:
            emoji = "🔴"

        with col2:
            st.metric("📊 Presupuesto", f"{emoji} {percentage:.1f}%")

        with col3:
            remaining = budget_limit - total_spent
            st.metric("💰 Disponible", f"${remaining:,.2f}")
    else:
        with col2:
            st.metric("📊 Presupuesto", "No configurado")
        with col3:
            st.metric("💰 Disponible", "-")

    # Transacciones
    with col4:
        count = len(df) if not df.empty else 0
        st.metric("🧾 Transacciones", count)


def show_expenses_by_card(df):
    """Gráfico de gastos por tarjeta."""
    if df.empty:
        st.info("No hay transacciones para mostrar")
        return

    expenses_by_card = df.groupby('card_name')['amount'].sum().reset_index()

    fig = px.bar(
        expenses_by_card,
        x='card_name',
        y='amount',
        title='Gastos por Tarjeta',
        labels={'card_name': 'Tarjeta', 'amount': 'Monto (ARS)'},
        color='amount',
        color_continuous_scale='Reds'
    )

    fig.update_layout(showlegend=False)
    st.plotly_chart(fig, use_container_width=True)


def show_daily_expenses(df):
    """Gráfico de gastos diarios."""
    if df.empty:
        st.info("No hay transacciones para mostrar")
        return

    # Convertir fecha a datetime
    df['date'] = pd.to_datetime(df['date'])

    daily_expenses = df.groupby('date')['amount'].sum().reset_index()

    fig = px.line(
        daily_expenses,
        x='date',
        y='amount',
        title='Gastos Diarios',
        labels={'date': 'Fecha', 'amount': 'Monto (ARS)'},
        markers=True
    )

    fig.update_traces(line_color='#FF4B4B')
    st.plotly_chart(fig, use_container_width=True)


def show_transactions_table(df):
    """Tabla de transacciones."""
    if df.empty:
        st.info("No hay transacciones para mostrar")
        return

    st.subheader("📋 Últimas Transacciones")

    # Seleccionar columnas relevantes
    display_df = df[['date', 'description', 'card_name', 'amount', 'category']].copy()
    display_df['date'] = pd.to_datetime(display_df['date']).dt.strftime('%d/%m/%Y')
    display_df['amount'] = display_df['amount'].apply(lambda x: f"${x:,.2f}")

    # Renombrar columnas
    display_df.columns = ['Fecha', 'Descripción', 'Tarjeta', 'Monto', 'Categoría']

    st.dataframe(display_df, use_container_width=True, hide_index=True)


def add_manual_expense():
    """Formulario para agregar gasto manual."""
    st.subheader("➕ Agregar Gasto Manual")

    with st.form("manual_expense_form"):
        col1, col2 = st.columns(2)

        with col1:
            date = st.date_input("Fecha", datetime.now())
            description = st.text_input("Descripción", placeholder="Ej: Almacén del barrio")
            amount = st.number_input("Monto", min_value=0.0, step=100.0)

        with col2:
            category = st.text_input("Categoría", placeholder="Ej: Comida")
            notes = st.text_area("Notas (opcional)")

        submitted = st.form_submit_button("💾 Guardar", use_container_width=True)

        if submitted:
            if not description or amount <= 0:
                st.error("Por favor completa todos los campos obligatorios")
            else:
                try:
                    supabase.table('transactions').insert({
                        'bank': 'Manual',
                        'card_type': 'Efectivo',
                        'card_name': 'Efectivo',
                        'date': date.strftime('%Y-%m-%d'),
                        'description': description,
                        'amount': amount,
                        'currency': 'ARS',
                        'is_manual': True,
                        'category': category if category else None,
                        'notes': notes if notes else None
                    }).execute()

                    st.success("✅ Gasto agregado correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")


def configure_budget():
    """Configurar presupuesto mensual."""
    st.subheader("💰 Configurar Presupuesto")

    today = datetime.now()
    current_month = today.strftime('%Y-%m')

    # Obtener presupuesto actual
    budget = get_budget_for_month(current_month)

    with st.form("budget_form"):
        budget_limit = st.number_input(
            "Límite Mensual",
            min_value=0.0,
            step=1000.0,
            value=float(budget['budget_limit']) if budget else 0.0
        )

        col1, col2 = st.columns(2)
        with col1:
            gross_salary = st.number_input(
                "Salario Bruto (opcional)",
                min_value=0.0,
                step=1000.0,
                value=float(budget['gross_salary']) if budget and budget.get('gross_salary') else 0.0
            )

        with col2:
            net_salary = st.number_input(
                "Salario Neto (opcional)",
                min_value=0.0,
                step=1000.0,
                value=float(budget['net_salary']) if budget and budget.get('net_salary') else 0.0
            )

        notes = st.text_area(
            "Notas",
            value=budget['notes'] if budget and budget.get('notes') else ""
        )

        submitted = st.form_submit_button("💾 Guardar", use_container_width=True)

        if submitted:
            if budget_limit <= 0:
                st.error("El límite debe ser mayor a 0")
            else:
                try:
                    data = {
                        'year_month': current_month,
                        'budget_limit': budget_limit,
                        'gross_salary': gross_salary if gross_salary > 0 else None,
                        'net_salary': net_salary if net_salary > 0 else None,
                        'notes': notes if notes else None
                    }

                    if budget:
                        # Update
                        supabase.table('budget')\
                            .update(data)\
                            .eq('year_month', current_month)\
                            .execute()
                    else:
                        # Insert
                        supabase.table('budget').insert(data).execute()

                    st.success("✅ Presupuesto guardado correctamente")
                    st.rerun()
                except Exception as e:
                    st.error(f"Error al guardar: {e}")


def main():
    """Función principal."""

    # Header
    st.markdown('<p class="main-header">💰 Expense Tracker</p>', unsafe_allow_html=True)

    # Sidebar
    with st.sidebar:
        st.title("Menú")

        page = st.radio(
            "Navegación",
            ["📊 Dashboard", "➕ Agregar Gasto", "💰 Presupuesto"],
            label_visibility="collapsed"
        )

        st.markdown("---")
        st.markdown("### ℹ️ Info")
        st.markdown("**Mes actual**: " + datetime.now().strftime('%B %Y'))

    # Contenido según página seleccionada
    if page == "📊 Dashboard":
        # Obtener datos
        df = get_current_month_expenses()
        current_month = datetime.now().strftime('%Y-%m')
        budget = get_budget_for_month(current_month)

        # KPIs
        show_kpis(df, budget)

        st.markdown("---")

        # Gráficos
        col1, col2 = st.columns(2)

        with col1:
            show_expenses_by_card(df)

        with col2:
            show_daily_expenses(df)

        st.markdown("---")

        # Tabla
        show_transactions_table(df)

    elif page == "➕ Agregar Gasto":
        add_manual_expense()

    elif page == "💰 Presupuesto":
        configure_budget()


if __name__ == '__main__':
    main()
