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
        {"fecha": default_date, "descripcion": "", "monto": 0.0, "categoria": "Otros", "moneda": currency},
        {"fecha": default_date, "descripcion": "", "monto": 0.0, "categoria": "Otros", "moneda": currency},
        {"fecha": default_date, "descripcion": "", "monto": 0.0, "categoria": "Otros", "moneda": currency},
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
                # Construir objeto gasto
                fecha_obj = row['fecha']
                if isinstance(fecha_obj, str):
                    try:
                        fecha_obj = datetime.strptime(fecha_obj, '%Y-%m-%d').date()
                    except:
                        fecha_obj = date.today()
                
                # Period format: YYYY-MM
                period = f"{fecha_obj.year}-{fecha_obj.month:02d}"

                nuevo_gasto = {
                    'id': str(uuid.uuid4()),
                    'period': period,
                    'date': fecha_obj, # Serialización se maneja en storage
                    'description': desc,
                    'amount': monto,
                    'currency': row.get('moneda', 'ARS'),
                    'category': row.get('categoria', 'Otros'),
                    'pagado': False, # Default
                    'tipo': 'manual'
                }
                
                storage.save_gasto_manual(nuevo_gasto)
                count += 1
        
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
