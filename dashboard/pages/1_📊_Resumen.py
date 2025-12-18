import streamlit as st
import plotly.express as px
import pandas as pd
from datetime import datetime, date
from services.data_service import get_data_service
from services.cuotas_service import get_cuotas_service
from services.local_storage import get_local_storage

st.set_page_config(page_title="Dashboard", page_icon="📊", layout="wide")

def show_dashboard():
    st.title("📊 Resumen de Gastos")

    # Init service
    service = get_data_service()

    # --- Load Data ---
    with st.spinner("Cargando datos..."):
        df = service.get_transactions(limit=500)

    # --- Sidebar Filters ---
    with st.sidebar:
        st.header("Filtros")

        # Bank Filter (sin filtro de fecha)
        selected_bank = "Todos"
        if not df.empty and 'bank' in df.columns:
            # Get unique banks
            banks = sorted([b for b in df['bank'].unique() if b])
            if banks:
                banks.insert(0, "Todos")
                selected_bank = st.selectbox("Filtrar por Banco/Tarjeta", banks)

    if df.empty:
        st.info("No hay transacciones guardadas. Importá un resumen o cargá gastos.")
        return

    # Filter by bank only
    if selected_bank != "Todos":
        filtered_df = df[df['bank'] == selected_bank]
    else:
        filtered_df = df.copy()

    if filtered_df.empty:
        st.warning(f"⚠️ No hay transacciones para el banco seleccionado: {selected_bank}")
        return

    # --- CONFIGURAR SUELDO MENSUAL ---
    st.markdown("### 💵 Sueldo Mensual")

    storage = get_local_storage()
    current_date = datetime.now()
    current_period = f"{current_date.year}-{current_date.month:02d}"
    sueldo_vigente = storage.get_sueldo_vigente(current_period)
    sueldo_especifico = storage.load_sueldos().get(current_period, None)

    col_sueldo1, col_sueldo2 = st.columns([3, 1])
    with col_sueldo1:
        if sueldo_especifico is None and sueldo_vigente > 0:
            st.info(f"ℹ️ Usando sueldo vigente: ${sueldo_vigente:,.0f}. Podés cambiarlo abajo si querés.")

        nuevo_sueldo = st.number_input(
            "Tu sueldo mensual (se propagará automáticamente a todos los meses)",
            min_value=0.0,
            value=float(sueldo_vigente),
            step=10000.0,
            format="%.0f",
            help="Este sueldo se usará para calcular cuánto te queda disponible cada mes"
        )

    with col_sueldo2:
        if st.button("💾 Guardar", type="primary"):
            storage.save_sueldo(current_period, nuevo_sueldo)
            st.success(f"✅ Guardado: ${nuevo_sueldo:,.0f}")
            st.rerun()

    st.markdown("---")

    # --- AGREGAR GASTO MANUAL ---
    st.markdown("### ✏️ Agregar Gasto Manual Rápido")

    with st.form("gasto_rapido_resumen", clear_on_submit=True):
        col1, col2, col3, col4, col5 = st.columns([3, 2, 1, 1, 1])

        with col1:
            descripcion_rapida = st.text_input("Descripción", placeholder="Ej: Alquiler, Uber, etc.")

        with col2:
            monto_rapido = st.number_input("Monto", min_value=0.0, step=100.0, format="%.0f")

        with col3:
            # Selector de mes para el gasto
            months = [
                ('Enero', 1), ('Febrero', 2), ('Marzo', 3), ('Abril', 4),
                ('Mayo', 5), ('Junio', 6), ('Julio', 7), ('Agosto', 8),
                ('Septiembre', 9), ('Octubre', 10), ('Noviembre', 11), ('Diciembre', 12)
            ]
            current_date = datetime.now()
            selected_month_gasto = st.selectbox(
                "Mes",
                options=[m[0] for m in months],
                index=current_date.month - 1,
                key="month_gasto"
            )

        with col4:
            # Selector de año
            years = list(range(current_date.year - 1, current_date.year + 3))
            selected_year_gasto = st.selectbox(
                "Año",
                options=years,
                index=1,  # Año actual
                key="year_gasto"
            )

        with col5:
            submitted_gasto = st.form_submit_button("💾", type="primary", use_container_width=True)

        # Checkbox para replicar en meses futuros
        replicar_futuro = st.checkbox(
            "🔄 Replicar en meses futuros (gasto recurrente)",
            help="Copia este gasto a todos los meses siguientes hasta fin de año siguiente"
        )

        if submitted_gasto:
            if not descripcion_rapida or monto_rapido <= 0:
                st.error("⚠️ Completá descripción y monto")
            else:
                import uuid
                storage_gasto = get_local_storage()

                month_num = next(m[1] for m in months if m[0] == selected_month_gasto)
                period_gasto = f"{selected_year_gasto}-{month_num:02d}"

                # Si se marcó replicar, crear gastos para todos los meses futuros
                if replicar_futuro:
                    # Desde el mes seleccionado hasta diciembre del año siguiente
                    end_year = selected_year_gasto + 1
                    end_month = 12

                    current_year = selected_year_gasto
                    current_month = month_num

                    gastos_creados = 0
                    while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
                        period = f"{current_year}-{current_month:02d}"
                        nuevo_gasto = {
                            'id': str(uuid.uuid4()),
                            'period': period,
                            'date': date.today(),
                            'description': descripcion_rapida,
                            'amount': monto_rapido,
                            'currency': 'ARS',
                            'category': 'Otros',
                            'pagado': False,
                            'tipo': 'manual'
                        }
                        storage_gasto.save_gasto_manual(nuevo_gasto)
                        gastos_creados += 1

                        # Siguiente mes
                        current_month += 1
                        if current_month > 12:
                            current_month = 1
                            current_year += 1

                    st.success(f"✅ Gasto recurrente guardado! Se crearon {gastos_creados} gastos desde {selected_month_gasto} {selected_year_gasto}")
                else:
                    # Solo crear el gasto para el mes seleccionado
                    nuevo_gasto = {
                        'id': str(uuid.uuid4()),
                        'period': period_gasto,
                        'date': date.today(),
                        'description': descripcion_rapida,
                        'amount': monto_rapido,
                        'currency': 'ARS',
                        'category': 'Otros',
                        'pagado': False,
                        'tipo': 'manual'
                    }

                    storage_gasto.save_gasto_manual(nuevo_gasto)
                    st.success(f"✅ Gasto guardado en {selected_month_gasto} {selected_year_gasto}!")

                st.rerun()

    st.markdown("---")

    # --- GASTOS POR MES (Carpetas) ---
    st.markdown("### 📂 Gastos por Resumen")

    # Inicializar estado de meses ocultos
    if 'meses_ocultos' not in st.session_state:
        st.session_state.meses_ocultos = storage.load_meses_ocultos()

    # Obtener períodos de transacciones Y de cuotas propagadas
    cuotas_service = get_cuotas_service()
    todas_cuotas = cuotas_service.get_todas_las_cuotas_activas()

    # Agrupar por statement_period si existe, sino por fecha
    if 'statement_period' in filtered_df.columns:
        # Usar el período del resumen
        periods_from_transactions = set(filtered_df['statement_period'].dropna().unique())

        # Agregar períodos de cuotas propagadas
        if not todas_cuotas.empty:
            periods_from_cuotas = set(todas_cuotas['period'].unique())
        else:
            periods_from_cuotas = set()

        # Combinar ambos sets
        all_periods_set = periods_from_transactions | periods_from_cuotas
        periods = sorted(list(all_periods_set), reverse=True)

        # Si hay transacciones sin statement_period, agruparlas por fecha
        no_period_df = filtered_df[filtered_df['statement_period'].isna()]
        if not no_period_df.empty:
            no_period_df['month_year'] = pd.to_datetime(no_period_df['date']).dt.to_period('M')
            old_periods = sorted(no_period_df['month_year'].unique(), reverse=True)
            # Convertir a string para mezclar con periods
            old_periods_str = [str(p) for p in old_periods]
        else:
            old_periods_str = []

        all_periods = list(periods) + old_periods_str
    else:
        # Fallback: usar fecha de transacción
        filtered_df['month_year'] = pd.to_datetime(filtered_df['date']).dt.to_period('M')
        all_periods = [str(p) for p in sorted(filtered_df['month_year'].unique(), reverse=True)]

    month_translations = {
        'January': 'Enero', 'February': 'Febrero', 'March': 'Marzo',
        'April': 'Abril', 'May': 'Mayo', 'June': 'Junio',
        'July': 'Julio', 'August': 'Agosto', 'September': 'Septiembre',
        'October': 'Octubre', 'November': 'Noviembre', 'December': 'Diciembre'
    }

    for period in all_periods:
        # Obtener transacciones del período
        if 'statement_period' in filtered_df.columns and period in periods:
            month_df = filtered_df[filtered_df['statement_period'] == period]
            # Formatear nombre: "2024-12" -> "Diciembre 2024"
            year, month_num = period.split('-')
            month_names = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                          'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
            month_name = f"{month_names[int(month_num)]} {year}"
        else:
            # Transacciones antiguas sin statement_period
            month_df = filtered_df[filtered_df['month_year'].astype(str) == period]
            # Formatear desde Period
            period_obj = pd.Period(period)
            month_name = period_obj.strftime('%B %Y').capitalize()
            for eng, esp in month_translations.items():
                month_name = month_name.replace(eng, esp)

        # Obtener cuotas propagadas para este período
        cuotas_periodo = cuotas_service.get_cuotas_para_periodo(period, incluir_encontradas=False)

        # Obtener gastos manuales para este período
        storage = get_local_storage()
        gastos_manuales = storage.load_gastos_manuales()
        gastos_manuales_periodo = [g for g in gastos_manuales if g.get('period') == period]

        # Calcular totales del mes (transacciones + cuotas + manuales)
        # Transacciones: Usar adjusted_amount si existe y es válido, sino amount
        def get_amount(row):
            if pd.notna(row.get('adjusted_amount')) and row.get('adjusted_amount') != '':
                try:
                    return float(row.get('adjusted_amount'))
                except:
                    return float(row['amount'])
            return float(row['amount'])

        month_ars = sum(get_amount(row) for _, row in month_df[month_df['currency'] == 'ARS'].iterrows())
        month_usd = sum(get_amount(row) for _, row in month_df[month_df['currency'] == 'USD'].iterrows())
        month_count = len(month_df)

        # Cuotas: Usar adjusted_amount si existe
        def get_cuota_amount(c):
            if c.get('adjusted_amount') is not None and c.get('adjusted_amount') != '':
                try:
                    return float(c.get('adjusted_amount'))
                except:
                    return float(c.get('amount'))
            return float(c.get('amount'))

        cuotas_ars = sum(get_cuota_amount(c) for c in cuotas_periodo if c.get('currency') == 'ARS')
        cuotas_usd = sum(get_cuota_amount(c) for c in cuotas_periodo if c.get('currency') == 'USD')
        cuotas_count = len(cuotas_periodo)

        manuales_ars = sum(g['amount'] for g in gastos_manuales_periodo if g.get('currency') == 'ARS')
        manuales_usd = sum(g['amount'] for g in gastos_manuales_periodo if g.get('currency') == 'USD')
        manuales_count = len(gastos_manuales_periodo)

        total_ars = month_ars + cuotas_ars + manuales_ars
        total_usd = month_usd + cuotas_usd + manuales_usd
        total_count = month_count + cuotas_count + manuales_count

        # Mostrar como expander (carpeta expandible)
        label_parts = [f"📅 {month_name}"]
        if total_count > 0:
            label_parts.append(f"{total_count} transacciones")
            if cuotas_count > 0:
                label_parts[-1] += f" ({cuotas_count} cuotas futuras)"
            label_parts.append(f"(ARS ${total_ars:,.0f} | USD ${total_usd:,.0f})")
        else:
            continue  # Skip empty periods

        # Verificar si el mes está oculto
        if period in st.session_state.meses_ocultos:
            continue  # No mostrar meses ocultos

        # Botón para ocultar + Expander
        col_hide, col_expand = st.columns([1, 20])
        with col_hide:
            if st.button("👁️", key=f"hide_{period}", help="Ocultar este mes"):
                st.session_state.meses_ocultos.add(period)
                storage.save_meses_ocultos(st.session_state.meses_ocultos)
                st.rerun()

        with col_expand:
            with st.expander(" - ".join(label_parts)):
                # Obtener sueldo vigente para este período
                sueldo_mes = storage.get_sueldo_vigente(period)
                disponible = sueldo_mes - total_ars
                porcentaje_usado = (total_ars / sueldo_mes * 100) if sueldo_mes > 0 else 0

                # Métricas del mes (con sueldo y disponible)
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("💵 Sueldo", f"$ {sueldo_mes:,.0f}")
                with col2:
                    st.metric("💰 Gastado ARS", f"$ {total_ars:,.0f}")
                with col3:
                    color = "normal" if disponible >= 0 else "inverse"
                    st.metric("💚 Disponible", f"$ {disponible:,.0f}",
                             delta=f"{porcentaje_usado:.0f}% usado")
                with col4:
                    st.metric("💵 USD", f"USD {total_usd:,.0f}")

                # Alerta si te pasaste del presupuesto
                if sueldo_mes > 0 and disponible < 0:
                    st.error(f"🚨 Te pasaste ${abs(disponible):,.0f} del presupuesto este mes!")
                elif sueldo_mes > 0 and porcentaje_usado >= 90:
                    st.warning(f"⚠️ Ya gastaste el {porcentaje_usado:.0f}% del sueldo!")

                st.markdown("---")

                # --- TRANSACCIONES DEL MES ---
                st.markdown("#### 💳 Tarjetas y Débito (desde PDF)")
                if not month_df.empty:
                    for idx, row in month_df.iterrows():
                        # Layout: Desc | Monto | Cuotas | Banco | Acciones (Edit/Delete)
                        col1, col2, col3, col4, col5, col6 = st.columns([5, 2, 1, 1, 0.5, 0.5])
                        
                        # Definir ID y Estado de Edición
                        t_id = row.get('id')
                        is_editing = st.session_state.get(f"edit_trans_{t_id}", False)
                        
                        # Calcular monto display (tachado si hay ajuste distinto)
                        original_amt = float(row.get('amount', 0))
                        adjusted = row.get('adjusted_amount')
                        has_adjustment = pd.notna(adjusted) and adjusted != ''
                        
                        final_amt = float(adjusted) if has_adjustment else original_amt

                        with col1:
                            if row.get('notes'):
                                st.write(f"**{row.get('description', '')}**")
                                st.caption(f"📝 {row.get('notes')}")
                            else:
                                st.write(f"**{row.get('description', '')}**")
                        
                        with col2:
                            if has_adjustment and abs(final_amt - original_amt) > 0.01:
                                # Escapar signo $ para evitar que Streamlit lo interprete como LaTeX
                                st.markdown(f"~~\\${original_amt:,.0f}~~ ➡️ **\\${final_amt:,.0f}** {row.get('currency', 'ARS')}")
                            elif has_adjustment and final_amt == 0:
                                st.markdown(f"~~\\${original_amt:,.0f}~~ **ANULADO** 🚫")
                            else:
                                st.write(f"${original_amt:,.0f} {row.get('currency', 'ARS')}")
                        
                        with col3:
                            cuotas_text = row.get('installments', '')
                            if cuotas_text:
                                st.write(f"🔢 {cuotas_text}")
                        
                        with col4:
                            st.write(f"_{row.get('bank', '')}_")
                            
                        with col5:
                            # Botón Editar
                            if st.button("✏️", key=f"btn_edit_trans_{t_id}", help="Editar notas/categoría"):
                                st.session_state[f"edit_trans_{t_id}"] = True
                                st.rerun()

                        with col6:
                            # Botón Eliminar
                            if st.button("🗑️", key=f"btn_del_trans_{t_id}", help="Eliminar transacción"):
                                if service.delete_transaction(t_id):
                                    st.success("Eliminado")
                                    st.rerun()
                                else:
                                    st.error("Error al eliminar")

                        # Formulario de Edición
                        if is_editing:
                            with st.form(key=f"form_edit_trans_{t_id}"):
                                st.markdown("###### ✏️ Editar Transacción")
                                st.caption("💡 Deja 'Monto Ajustado' vacío o igual al original para restaurar.")
                                
                                new_notes = st.text_area("Notas / Comentarios", value=row.get('notes') or "")
                                new_category = st.text_input("Categoría", value=row.get('category') or "")
                                
                                # Input para Adjusted Amount
                                current_adj = float(adjusted) if has_adjustment else float(original_amt)
                                new_adjusted = st.number_input("Monto Ajustado (0 para anular)", value=current_adj, step=100.0)

                                c1, c2 = st.columns(2)
                                with c1:
                                    if st.form_submit_button("💾 Guardar", type="primary"):
                                        update_data = {
                                            'notes': new_notes,
                                            'category': new_category,
                                            'adjusted_amount': new_adjusted
                                        }
                                        service.update_transaction(t_id, update_data)
                                        st.session_state[f"edit_trans_{t_id}"] = False
                                        st.success("Guardado!")
                                        st.rerun()
                                with c2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f"edit_trans_{t_id}"] = False
                                        st.rerun()
                            st.markdown("---")

                else:
                    st.info("No hay transacciones de tarjeta este mes")

                st.markdown("---")

                # --- CUOTAS PROPAGADAS ---
                if cuotas_periodo:
                    st.markdown("#### 🔄 Cuotas Futuras Proyectadas")
                    for cuota in cuotas_periodo:
                        # Layout: Desc | Monto | Cuotas | Banco | Acciones (Edit/Delete)
                        col1, col2, col3, col4, col5, col6 = st.columns([5, 2, 1, 1, 0.5, 0.5])
                        
                        # ID único para cuota propagada (original_id + periodo)
                        c_unique_id = f"{cuota.get('original_id')}_{period}"
                        is_editing_cuota = st.session_state.get(f"edit_cuota_{c_unique_id}", False)

                        # Montos con lógica de ajuste
                        original_amt = float(cuota.get('amount', 0))
                        adjusted = cuota.get('adjusted_amount')
                        has_adjustment = adjusted is not None and adjusted != ''
                        final_amt = float(adjusted) if has_adjustment else original_amt

                        with col1:
                            if cuota.get('notes'):
                                st.write(f"**{cuota.get('description', '')}**")
                                st.caption(f"📝 {cuota.get('notes')}")
                            else:
                                st.write(f"**{cuota.get('description', '')}**")

                        with col2:
                            if has_adjustment and abs(final_amt - original_amt) > 0.01:
                                # Escapar signo $ para evitar que Streamlit lo interprete como LaTeX
                                st.markdown(f"~~\\${original_amt:,.0f}~~ ➡️ **\\${final_amt:,.0f}** {cuota.get('currency', 'ARS')}")
                            elif has_adjustment and final_amt == 0:
                                st.markdown(f"~~\\${original_amt:,.0f}~~ **ANULADO** 🚫")
                            else:
                                st.write(f"${original_amt:,.0f} {cuota.get('currency', 'ARS')}")

                        with col3:
                            st.write(f"🔢 {cuota.get('installments', '')}")
                        with col4:
                            st.write(f"_{cuota.get('bank', '')}_")
                            
                        with col5:
                             # Botón Editar
                            if st.button("✏️", key=f"btn_edit_cuota_{c_unique_id}", help="Editar notas futuras"):
                                st.session_state[f"edit_cuota_{c_unique_id}"] = True
                                st.rerun()

                        with col6:
                            # Botón Eliminar (Anular propagación específica)
                            if st.button("🗑️", key=f"btn_del_cuota_{c_unique_id}", help="Eliminar/Ocultar esta cuota"):
                                if storage.delete_cuota_propagada(cuota.get('original_id'), period):
                                    st.success("Cuota eliminada de la vista")
                                    st.rerun()
                        
                        # Formulario de Edición Cuota
                        if is_editing_cuota:
                            with st.form(key=f"form_edit_cuota_{c_unique_id}"):
                                st.markdown("###### ✏️ Editar Cuota Futura")
                                st.info("ℹ️ Esto solo modifica esta cuota específica, no todas las futuras.")
                                new_notes = st.text_area("Notas / Comentarios", value=cuota.get('notes') or "")
                                new_category = st.text_input("Categoría", value=cuota.get('category') or "")
                                
                                # Input para Adjusted Amount Cuota
                                current_adj_cuota = float(adjusted) if has_adjustment else float(original_amt)
                                new_adjusted_cuota = st.number_input("Monto Ajustado (0 para anular)", value=current_adj_cuota, step=100.0)

                                c1, c2 = st.columns(2)
                                with c1:
                                    if st.form_submit_button("💾 Guardar", type="primary"):
                                        storage.update_cuota_propagada(
                                            cuota.get('original_id'),
                                            period,
                                            {
                                                'notes': new_notes,
                                                'category': new_category,
                                                'adjusted_amount': new_adjusted_cuota
                                            }
                                        )
                                        st.session_state[f"edit_cuota_{c_unique_id}"] = False
                                        st.success("Guardado!")
                                        st.rerun()
                                with c2:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f"edit_cuota_{c_unique_id}"] = False
                                        st.rerun()
                            st.markdown("---")

                    st.markdown("---")

                # --- GASTOS MANUALES ---
                if gastos_manuales_periodo:
                    st.markdown("#### ✏️ Gastos Manuales")
                    for gasto in gastos_manuales_periodo:
                        col1, col2, col3, col4 = st.columns([4, 2, 1, 1])
                        with col1:
                            st.write(f"**{gasto.get('description', '')}**")
                        with col2:
                            st.write(f"${gasto.get('amount', 0):,.0f}")
                        with col3:
                            # Botón editar
                            if st.button("✏️", key=f"edit_{gasto['id']}", help="Editar"):
                                st.session_state[f"editing_{gasto['id']}"] = True
                                st.rerun()
                        with col4:
                            # Botón eliminar
                            if st.button("🗑️", key=f"delete_{gasto['id']}", help="Eliminar"):
                                # Eliminar el gasto
                                storage_delete = get_local_storage()
                                gastos_all = storage_delete.load_gastos_manuales()
                                gastos_all = [g for g in gastos_all if g['id'] != gasto['id']]
                                # Guardar lista actualizada
                                import json
                                with open(storage_delete.gastos_manuales_file, 'w') as f:
                                    json.dump(gastos_all, f, indent=2, default=storage_delete._serialize_date)
                                st.success("✅ Gasto eliminado")
                                st.rerun()

                        # Si está en modo edición, mostrar formulario
                        if st.session_state.get(f"editing_{gasto['id']}", False):
                            with st.form(key=f"edit_form_{gasto['id']}"):
                                st.markdown("**Editar Gasto:**")
                                nueva_desc = st.text_input("Descripción", value=gasto.get('description', ''))
                                nuevo_monto = st.number_input("Monto", value=float(gasto.get('amount', 0)), step=100.0, format="%.0f")

                                col_save, col_cancel = st.columns(2)
                                with col_save:
                                    if st.form_submit_button("💾 Guardar", type="primary"):
                                        # Actualizar gasto
                                        storage_edit = get_local_storage()
                                        storage_edit.update_gasto_manual(gasto['id'], {
                                            'description': nueva_desc,
                                            'amount': nuevo_monto
                                        })
                                        st.session_state[f"editing_{gasto['id']}"] = False
                                        st.success("✅ Gasto actualizado")
                                        st.rerun()
                                with col_cancel:
                                    if st.form_submit_button("❌ Cancelar"):
                                        st.session_state[f"editing_{gasto['id']}"] = False
                                        st.rerun()

                if not month_df.empty or cuotas_periodo or gastos_manuales_periodo:
                    pass  # Ya mostramos todo arriba
                else:
                    st.info("No hay transacciones en este período")

    # Botón para mostrar meses ocultos
    if st.session_state.meses_ocultos:
        st.markdown("---")
        st.markdown(f"### 👁️ Meses Ocultos ({len(st.session_state.meses_ocultos)})")

        cols = st.columns(min(len(st.session_state.meses_ocultos), 5))
        for idx, period_oculto in enumerate(sorted(st.session_state.meses_ocultos, reverse=True)):
            with cols[idx % 5]:
                # Formatear nombre del mes
                try:
                    year, month_num = period_oculto.split('-')
                    month_names = ['', 'Enero', 'Febrero', 'Marzo', 'Abril', 'Mayo', 'Junio',
                                  'Julio', 'Agosto', 'Septiembre', 'Octubre', 'Noviembre', 'Diciembre']
                    month_name_oculto = f"{month_names[int(month_num)]} {year}"
                except:
                    month_name_oculto = period_oculto

                if st.button(f"👁️ {month_name_oculto}", key=f"show_{period_oculto}", use_container_width=True):
                    st.session_state.meses_ocultos.remove(period_oculto)
                    storage.save_meses_ocultos(st.session_state.meses_ocultos)
                    st.rerun()

if __name__ == "__main__":
    show_dashboard()
