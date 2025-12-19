import streamlit as st
import pandas as pd
from datetime import datetime, date
import uuid
from services.local_storage import get_local_storage

st.set_page_config(page_title="Carga Manual", page_icon="✏️", layout="wide")

def show_manual_load():
    st.title("✏️ Carga Manual de Gastos")
    st.markdown("Agregá múltiples gastos a la vez usando la tabla interactiva.")

    # --- Configuración Inicial ---
    col1, col2 = st.columns(2)
    current_date = datetime.now()
    
    with col1:
        default_date = st.date_input("Fecha por defecto", value=current_date)
    
    with col2:
        currency = st.selectbox("Moneda por defecto", ["ARS", "USD"])

    # --- Data Editor ---
    st.markdown("### 📝 Ingresá los gastos")
    st.info("💡 Podés copiar y pegar desde Excel o Sheets. Agregá filas con el botón '+'.")

    # Estructura inicial del DataFrame
    # Pre-llenamos con 3 filas vacías para invitar a la acción
    initial_data = [
        {"fecha": default_date, "descripcion": "", "monto": 0.0, "categoria": "Otros", "moneda": currency, "recurrente": False},
        {"fecha": default_date, "descripcion": "", "monto": 0.0, "categoria": "Otros", "moneda": currency, "recurrente": False},
        {"fecha": default_date, "descripcion": "", "monto": 0.0, "categoria": "Otros", "moneda": currency, "recurrente": False},
    ]
    
    df = pd.DataFrame(initial_data)

    edited_df = st.data_editor(
        df,
        num_rows="dynamic",
        use_container_width=True,
        column_config={
            "fecha": st.column_config.DateColumn(
                "Fecha",
                format="DD/MM/YYYY",
                required=True,
                default=default_date
            ),
            "descripcion": st.column_config.TextColumn(
                "Descripción",
                required=True
            ),
            "monto": st.column_config.NumberColumn(
                "Monto",
                required=True,
                format="$ %.2f",
                min_value=0.0
            ),
            "categoria": st.column_config.SelectboxColumn(
                "Categoría",
                options=[
                    'Supermercado', 'Restaurante', 'Servicios', 
                    'Transporte', 'Entretenimiento', 'Shopping', 
                    'Suscripciones', 'Viajes', 'Otros'
                ],
                required=True,
                default="Otros"
            ),
            "moneda": st.column_config.SelectboxColumn(
                "Moneda",
                options=["ARS", "USD"],
                required=True,
                default=currency
            ),
            "recurrente": st.column_config.CheckboxColumn(
                "Recurrente?",
                help="Si se marca, se repite hasta fin del año siguiente",
                default=False
            )
        },
        key="editor_gastos_manuales"
    )

    # --- Guardado ---
    if st.button("💾 Guardar Todos los Gastos", type="primary", use_container_width=True):
        storage = get_local_storage()
        count = 0
        
        # Iterar sobre las filas editadas
        for index, row in edited_df.iterrows():
            # Validar que tenga descripción y monto > 0
            # Pandas a veces deja NaNs o strings vacíos
            desc = str(row.get('descripcion', '')).strip()
            try:
                monto = float(row.get('monto', 0))
            except:
                monto = 0.0
                
            if desc and monto > 0:
                # Construir objeto gasto base
                fecha_obj = row['fecha']
                if isinstance(fecha_obj, str):
                    try:
                        fecha_obj = datetime.strptime(fecha_obj, '%Y-%m-%d').date()
                    except:
                        fecha_obj = date.today()
                
                es_recurrente = row.get('recurrente', False)
                
                # Definir rango de periodos
                year_start = fecha_obj.year
                month_start = fecha_obj.month
                
                if es_recurrente:
                    # Hasta diciembre del año siguiente
                    end_year = year_start + 1
                    end_month = 12
                else:
                    # Solo una vez
                    end_year = year_start
                    end_month = month_start

                current_year = year_start
                current_month = month_start
                
                while (current_year < end_year) or (current_year == end_year and current_month <= end_month):
                    # Calcular fecha para este periodo (mismo día o fin de mes)
                    # Simplificación: Usamos el día 1 o la misma fecha original si es posible, 
                    # pero `period` es lo importante. `date` se usa para ordenar.
                    
                    try:
                        fecha_actual = date(current_year, current_month, fecha_obj.day)
                    except ValueError:
                        # Si el día no existe (ej: 31 de feb), usar el último día del mes
                        if current_month == 12:
                             fecha_actual = date(current_year, current_month, 31)
                        else:
                             # Truco: día 1 del mes siguiente menos 1 día
                             # Pero simple fallback: día 28
                             fecha_actual = date(current_year, current_month, 28)

                    period = f"{current_year}-{current_month:02d}"

                    nuevo_gasto = {
                        'id': str(uuid.uuid4()),
                        'period': period,
                        'date': fecha_actual, 
                        'description': desc,
                        'amount': monto,
                        'currency': row.get('moneda', 'ARS'),
                        'category': row.get('categoria', 'Otros'),
                        'pagado': False, 
                        'tipo': 'manual'
                    }
                    
                    storage.save_gasto_manual(nuevo_gasto)
                    count += 1
                    
                    # Avanzar mes
                    current_month += 1
                    if current_month > 12:
                        current_month = 1
                        current_year += 1
                    
                    # Romper loop si no es recurrente (redundante con condición while pero seguro)
                    if not es_recurrente:
                        break
        
        if count > 0:
            st.success(f"✅ Se guardaron {count} gastos correctamente.")
            st.balloons()
            # Limpiar estado si fuera posible, pero st.data_editor mantiene estado.
            # Una forma de limpiar es setear una key nueva o usar on_change, pero rerun limpia logs.
            import time
            time.sleep(1)
            st.rerun()
        else:
            st.warning("⚠️ No se encontraron filas válidas para guardar (monto > 0 y descripción requerida).")

if __name__ == "__main__":
    show_manual_load()
