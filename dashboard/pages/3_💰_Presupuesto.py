import streamlit as st
import pandas as pd
from datetime import datetime, date
from services.data_service import get_data_service
from services.cuotas_service import get_cuotas_service
from services.local_storage import get_local_storage

st.set_page_config(page_title="Presupuesto", page_icon="💰", layout="wide")

def show_presupuesto():
    st.title("💰 Presupuesto y Gastos")

    # Init service
    service = get_data_service()

    # Selector de mes
    st.markdown("### 📅 Seleccionar Período")
    col_month, col_year = st.columns(2)

    current_date = datetime.now()
    months = [
        ('Enero', 1), ('Febrero', 2), ('Marzo', 3), ('Abril', 4),
        ('Mayo', 5), ('Junio', 6), ('Julio', 7), ('Agosto', 8),
        ('Septiembre', 9), ('Octubre', 10), ('Noviembre', 11), ('Diciembre', 12)
    ]

    with col_month:
        selected_month = st.selectbox(
            "Mes",
            options=[m[0] for m in months],
            index=current_date.month - 1
        )

    with col_year:
        # Incluir años futuros para poder ver cuotas propagadas
        years = list(range(current_date.year + 2, current_date.year - 3, -1))
        selected_year = st.selectbox("Año", options=years, index=2)  # Index 2 = año actual

    month_num = next(m[1] for m in months if m[0] == selected_month)
    period = f"{selected_year}-{month_num:02d}"

    st.markdown("---")

    # --- SUELDO DEL MES ---
    st.markdown("### 💵 Sueldo del Mes")

    # Inicializar storage
    storage = get_local_storage()

    # Obtener sueldo vigente para este período (busca hacia atrás si no hay uno específico)
    sueldo_vigente = storage.get_sueldo_vigente(period)
    sueldo_especifico = storage.load_sueldos().get(period, None)

    col1, col2 = st.columns([3, 1])
    with col1:
        # Mostrar mensaje si está usando sueldo heredado
        if sueldo_especifico is None and sueldo_vigente > 0:
            st.info(f"ℹ️ Usando sueldo vigente: ${sueldo_vigente:,.0f}. Podés cambiarlo para este mes abajo.")

        nuevo_sueldo = st.number_input(
            f"Sueldo de {selected_month} {selected_year}",
            min_value=0.0,
            value=float(sueldo_vigente),
            step=10000.0,
            format="%.0f",
            help="El sueldo se propagará automáticamente a meses futuros hasta que lo cambies"
        )

    with col2:
        if st.button("💾 Guardar Sueldo", type="primary"):
            storage.save_sueldo(period, nuevo_sueldo)
            st.success(f"✅ Sueldo guardado: ${nuevo_sueldo:,.0f}")
            st.info("Este sueldo se usará para este mes y todos los meses futuros hasta que lo cambies.")
            st.rerun()

    st.markdown("---")

    # --- GASTOS MANUALES ---
    st.markdown("### ✏️ Agregar Gasto Manual")
    st.info("Usá esto para gastos que no aparecen en resúmenes de tarjeta (efectivo, débito, transferencias, etc.)")

    with st.form("gasto_manual_form"):
        col1, col2, col3 = st.columns(3)

        with col1:
            descripcion = st.text_input("Descripción", placeholder="Ej: Alquiler, Expensas, etc.")

        with col2:
            monto = st.number_input("Monto (ARS)", min_value=0.0, step=100.0, format="%.0f")

        with col3:
            categoria = st.selectbox(
                "Categoría",
                options=[
                    'Vivienda', 'Servicios', 'Transporte', 'Supermercado',
                    'Salud', 'Educación', 'Entretenimiento', 'Otros'
                ]
            )

        col4, col5 = st.columns(2)
        with col4:
            fecha_gasto = st.date_input("Fecha", value=date.today())

        with col5:
            pagado = st.checkbox("✅ Ya pagado", value=False)

        submitted = st.form_submit_button("💾 Agregar Gasto", type="primary")

        if submitted:
            if not descripcion:
                st.error("⚠️ Por favor ingresá una descripción")
            elif monto <= 0:
                st.error("⚠️ El monto debe ser mayor a 0")
            else:
                import uuid
                storage_temp = get_local_storage()

                nuevo_gasto = {
                    'id': str(uuid.uuid4()),
                    'period': period,
                    'date': fecha_gasto,
                    'description': descripcion,
                    'amount': monto,
                    'currency': 'ARS',
                    'category': categoria,
                    'pagado': pagado,
                    'tipo': 'manual'
                }

                storage_temp.save_gasto_manual(nuevo_gasto)
                st.success(f"✅ Gasto agregado: {descripcion} - ${monto:,.0f}")
                st.rerun()

    st.markdown("---")

    # --- RESUMEN DEL MES ---
    st.markdown("### 📊 Resumen del Período")

    # Inicializar servicios
    cuotas_service = get_cuotas_service()
    storage = get_local_storage()

    # Obtener gastos de tarjetas para este período
    df_tarjetas = service.get_transactions(limit=500)
    if not df_tarjetas.empty and 'statement_period' in df_tarjetas.columns:
        gastos_tarjetas = df_tarjetas[df_tarjetas['statement_period'] == period]
        total_tarjetas = gastos_tarjetas[gastos_tarjetas['currency'] == 'ARS']['amount'].sum()
    else:
        total_tarjetas = 0.0

    # Obtener cuotas propagadas para este período (cuotas futuras que aún no están en PDF)
    cuotas_propagadas = cuotas_service.get_cuotas_para_periodo(period, incluir_encontradas=False)
    total_cuotas_propagadas = sum(c['amount'] for c in cuotas_propagadas if c.get('currency') == 'ARS')

    # Obtener gastos manuales para este período
    gastos_manuales_periodo = storage.load_gastos_manuales()
    gastos_manuales_periodo = [g for g in gastos_manuales_periodo if g.get('period') == period]

    total_manuales = sum(g['amount'] for g in gastos_manuales_periodo)
    total_manuales_pagados = sum(g['amount'] for g in gastos_manuales_periodo if g.get('pagado', False))
    total_manuales_pendientes = sum(g['amount'] for g in gastos_manuales_periodo if not g.get('pagado', False))

    # Total general (incluye cuotas propagadas)
    total_gastos = total_tarjetas + total_cuotas_propagadas + total_manuales
    sueldo = storage.get_sueldo_vigente(period)  # Usar sueldo vigente (propaga automáticamente)
    disponible = sueldo - total_gastos
    porcentaje_usado = (total_gastos / sueldo * 100) if sueldo > 0 else 0

    # Métricas
    col1, col2, col3, col4, col5 = st.columns(5)

    with col1:
        st.metric("💵 Sueldo", f"$ {sueldo:,.0f}")

    with col2:
        st.metric("💳 Tarjetas (PDF)", f"$ {total_tarjetas:,.0f}")

    with col3:
        cuotas_count = len(cuotas_propagadas)
        st.metric("🔄 Cuotas Futuras", f"$ {total_cuotas_propagadas:,.0f}",
                 delta=f"{cuotas_count} cuotas" if cuotas_count > 0 else None,
                 help="Cuotas que se van a cargar en este mes")

    with col4:
        st.metric("✏️ Gastos Manuales", f"$ {total_manuales:,.0f}")

    with col5:
        delta_color = "normal" if disponible >= 0 else "inverse"
        st.metric("💰 Disponible", f"$ {disponible:,.0f}", delta=f"{porcentaje_usado:.1f}% usado")

    # Alertas
    if sueldo > 0:
        if porcentaje_usado >= 100:
            st.error(f"🚨 **ALERTA CRÍTICA**: ¡Te pasaste del presupuesto! Gastaste ${total_gastos - sueldo:,.0f} más de lo que tenés.")
        elif porcentaje_usado >= 90:
            st.warning(f"⚠️ **CUIDADO**: Ya gastaste el {porcentaje_usado:.1f}% de tu sueldo. Solo te quedan ${disponible:,.0f}")
        elif porcentaje_usado >= 75:
            st.info(f"ℹ️ **Atención**: Llevás gastado el {porcentaje_usado:.1f}% del presupuesto.")

    st.markdown("---")

    # --- BARRA DE PROGRESO ---
    if sueldo > 0:
        st.markdown("### 📈 Uso del Presupuesto")
        progress_value = min(porcentaje_usado / 100, 1.0)
        st.progress(progress_value, text=f"{porcentaje_usado:.1f}% del presupuesto usado")

    st.markdown("---")

    # --- LISTA DE GASTOS MANUALES ---
    if gastos_manuales_periodo:
        st.markdown("### 📝 Gastos Manuales del Período")

        # Mostrar pendientes primero
        pendientes = [g for g in gastos_manuales_periodo if not g['pagado']]
        pagados = [g for g in gastos_manuales_periodo if g['pagado']]

        if pendientes:
            st.markdown("#### ⏳ Pendientes de Pago")
            for gasto in pendientes:
                col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

                with col1:
                    st.write(f"**{gasto['description']}**")
                with col2:
                    st.write(f"${gasto['amount']:,.0f}")
                with col3:
                    st.write(f"{gasto['category']}")
                with col4:
                    if st.button("✅", key=f"pay_{gasto['id']}", help="Marcar como pagado"):
                        # Actualizar estado usando LocalStorage
                        storage_update = get_local_storage()
                        storage_update.update_gasto_manual(gasto['id'], {'pagado': True})
                        st.rerun()

        if pagados:
            with st.expander(f"✅ Pagados ({len(pagados)}) - Total: ${total_manuales_pagados:,.0f}"):
                for gasto in pagados:
                    col1, col2, col3 = st.columns([3, 2, 2])

                    with col1:
                        st.write(f"~~{gasto['description']}~~")
                    with col2:
                        st.write(f"~~${gasto['amount']:,.0f}~~")
                    with col3:
                        st.write(f"~~{gasto['category']}~~")

    # --- CUOTAS PROPAGADAS ---
    if cuotas_propagadas:
        st.markdown("---")
        st.markdown("### 🔄 Cuotas Proyectadas para Este Mes")
        st.info(f"💡 Estas son cuotas de compras anteriores que se van a cobrar este mes. Total: {len(cuotas_propagadas)} cuotas")

        for cuota in cuotas_propagadas:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 1])

            with col1:
                st.write(f"**{cuota['description']}**")
            with col2:
                st.write(f"${cuota['amount']:,.0f}")
            with col3:
                st.write(f"{cuota['bank']}")
            with col4:
                st.write(f"🔢 {cuota['installments']}")

if __name__ == "__main__":
    show_presupuesto()
