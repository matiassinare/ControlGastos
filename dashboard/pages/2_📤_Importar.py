import streamlit as st
import pandas as pd
import pdfplumber
import re
import sys
from pathlib import Path
from datetime import datetime
from services.data_service import get_data_service
from services.cuotas_service import get_cuotas_service

# Agregar path al scraper para importar los parsers
scraper_path = Path(__file__).parent.parent.parent / 'scraper'
if str(scraper_path) not in sys.path:
    sys.path.insert(0, str(scraper_path))

st.set_page_config(page_title="Importar Resumen", page_icon="📤", layout="wide")

def detect_bank_from_pdf(file):
    """Detectar qué banco es el PDF."""
    with pdfplumber.open(file) as pdf:
        if pdf.pages:
            text = pdf.pages[0].extract_text()
            if text:
                upper_text = text.upper()

                # Galicia Visa - buscar múltiples indicadores
                if 'GALICIA' in upper_text and 'VISA' in upper_text:
                    return 'GALICIA_VISA'
                # Galicia sin nombre explícito pero con formato característico
                elif 'DETALLE DEL CONSUMO' in upper_text and 'TARJETA CRÉDITO VISA' in upper_text and 'CUOTA' in upper_text:
                    return 'GALICIA_VISA'
                # Galicia Amex
                elif 'GALICIA' in upper_text and ('AMEX' in upper_text or 'AMERICAN EXPRESS' in upper_text):
                    return 'GALICIA_AMEX'
                elif 'DETALLE DEL CONSUMO' in upper_text and 'AMERICAN EXPRESS' in upper_text:
                    return 'GALICIA_AMEX'
                # BBVA
                elif 'BBVA' in upper_text or 'FRANCES' in upper_text:
                    return 'BBVA'
    return 'GENERIC'

def parse_galicia_pdf(file, card_type='Visa'):
    """Usar el parser específico de Galicia."""
    try:
        from banks.galicia_pdf_parser import GaliciaPDFParser

        # Guardar temporalmente el archivo
        import tempfile
        with tempfile.NamedTemporaryFile(delete=False, suffix='.pdf') as tmp_file:
            tmp_file.write(file.read())
            tmp_path = tmp_file.name

        # Parsear con el parser específico
        parser = GaliciaPDFParser(tmp_path)
        transactions = parser.parse(card_type)

        # Limpiar archivo temporal
        Path(tmp_path).unlink()

        # Convertir al formato esperado por el dashboard
        formatted_transactions = []
        for t in transactions:
            formatted_transactions.append({
                'date': datetime.strptime(t['date'], '%Y-%m-%d').date(),
                'description': t['description'],
                'amount': t['amount'],
                'currency': t['currency'],
                'installments': t.get('cuota', '1/1'),
                'category': t.get('category', 'Otros'),
                'bank': f"Galicia {t['card_type']}"
            })

        return formatted_transactions, True
    except Exception as e:
        st.error(f"Error usando parser de Galicia: {e}")
        return [], False

def parse_pdf_content(file):
    """
    Intenta parsear transacciones de un PDF.
    Esta es una implementación genérica inicial que busca patrones de fechas y montos.
    """
    transactions = []
    text_content = ""
    detected_bank = "Desconocido"
    
    # Keywords for bank detection
    bank_keywords = {
        'BBVA': ['BBVA', 'FRANCES'],
        'GALICIA': ['GALICIA'],
        'SANTANDER': ['SANTANDER', 'RIO'],
        'AMEX': ['AMERICAN EXPRESS', 'AMEX'],
        'VISA': ['VISA'],
        'MASTERCARD': ['MASTERCARD', 'MASTER'],
        'NACION': ['NACION'],
        'MACRO': ['MACRO']
    }
    
    with pdfplumber.open(file) as pdf:
        for i, page in enumerate(pdf.pages):
            text = page.extract_text()
            if text:
                text_content += text + "\n"
                
                # Try to detect bank in the first page
                if i == 0:
                    upper_text = text.upper()
                    for bank, keywords in bank_keywords.items():
                        if any(k in upper_text for k in keywords):
                            detected_bank = bank
                            break
                            
                # Regex optimizado para BBVA / Visa (formato: 13-Mar-25 COPPEL... 91.666,58)
                # Busca fechas como DD-Mon-YY
                # Meses posibles: Ene, Feb, Mar, Abr, May, Jun, Jul, Ago, Sep, Oct, Nov, Dic (y sus variantes en inglés si las hubiera)
                
                months_map = {
                    'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04', 'May': '05', 'Jun': '06',
                    'Jul': '07', 'Ago': '08', 'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12',
                    'Jan': '01', 'Apr': '04', 'Aug': '08', 'Dec': '12' # English fallback just in case
                }
                
                lines = text.split('\n')
                lines = text.split('\n')
                ignored_keywords = [
                    'SALDO ACTUAL', 'CIERRE ACTUAL', 'TOTAL CONSUMOS', 
                    'SU PAGO EN', 'VENCIMIENTO ACTUAL', 'DE COMPRA',
                    'DE FINANCIACIÓN', 'DE ADELANTO', 'TOTAL DE CUOTAS',
                    'TASAS', 'DETALLE', 'SOBRE'
                ]
                
                for line in lines:
                    # Skip summary/header lines
                    if any(keyword in line.upper() for keyword in ignored_keywords):
                        continue

                    # Regex para fecha DD-Mon-YY
                    date_match = re.search(r'(\d{2})-([A-Za-z]{3})-(\d{2})', line)
                    
                    if date_match:
                        day, month_str, year = date_match.groups()
                        month_str = month_str.capitalize()
                        
                        if month_str in months_map:
                            month = months_map[month_str]
                            full_year = f"20{year}"
                            try:
                                date_obj = datetime.strptime(f"{day}/{month}/{full_year}", "%d/%m/%Y").date()
                            except ValueError:
                                continue # Invalid date
                            
                            # Limpiar la fecha de la línea
                            rest = line.replace(date_match.group(0), '').strip()
                            
                            # Detectar y limpiar segunda fecha si existe (ej: vencimientos)
                            rest = re.sub(r'\d{2}-[A-Za-z]{3}-\d{2}', '', rest)
                            
                            # Ignorar montos entre paréntesis (bases imponibles de impuestos)
                            rest = re.sub(r'\(.*?\)', '', rest)
                            
                            # Detectar Cuotas (ej: C.09/12)
                            installments = "1/1"
                            inst_match = re.search(r'C\.(\d{1,2})/(\d{1,2})', rest)
                            if inst_match:
                                current, total = inst_match.groups()
                                installments = f"{int(current)}/{int(total)}"
                                # Removed from text to clean description
                                rest = rest.replace(inst_match.group(0), "")
                            
                            # Buscar montos
                            number_pattern = r'(-?[\d\.]+,\d{2})'
                            matches = re.findall(number_pattern, rest)
                            
                            if matches:
                                is_usd = "USD" in rest or "U$S" in rest
                                
                                # Limpieza de descripción
                                description = rest
                                for m in matches:
                                    description = description.replace(m, "")
                                
                                description = description.replace("USD", "").replace("U$S", "").strip()
                                # Remove long numeric refs (coupons)
                                description = re.sub(r'\s\d{6,}\s', ' ', description)
                                description = re.sub(r'^\d+\s', '', description) # Remove leading numbers
                                description = description.strip()
                                
                                # Skip if description is empty or too short
                                if len(description) < 3:
                                    continue

                                # Deduplicate logic:
                                # For "USD 14,99 ... 14,99", we want only one transaction of 14.99 USD
                                unique_amounts = []
                                seen_vals = set()
                                
                                for m in matches:
                                    val_clean = m.replace('.', '').replace(',', '.')
                                    # Handle negative numbers parsing quirks if necessary
                                    if val_clean not in seen_vals:
                                        unique_amounts.append(m)
                                        seen_vals.add(val_clean)
                                
                                # Process specific matches
                                # If we have 2 different amounts, usually ARS then USD, OR TaxBase then Tax.
                                # But BBVA summary usually has: Desc | Coupon | PESOS | DOLARES
                                # If a line has both, we might want 2 transactions? No, usually it's one purchase.
                                # But distinct amounts in BBVA line usually mean:
                                # Col 1: Pesos, Col 2: Dolar.
                                # Example: "NETFLIX ... 0,00 15,99" -> 0 Pesos, 15.99 USD.
                                # Example: "COMPRA ... 1000,00" -> 1000 Pesos.
                                
                                # Special handling for BBVA 2-column format
                                # If matches has 2 elements, and one is 0,00, take the other.
                                # If both are non-zero and different? Rare for same transaction unless mixed payment?
                                # Let's assume matches map to [PESOS, DOLARES] positionally if lines correspond to headers.
                                # But regex loses position.
                                
                                # Safe logic for MVP:
                                # Iterate unique amounts.
                                # If is_usd is True, assume the amount found is USD.
                                # If duplicate amounts existed (14.99 twice), we already deduped.
                                
                                for amount_str in unique_amounts:
                                    try:
                                        val_str = amount_str.replace('.', '').replace(',', '.')
                                        if val_str.count('-') > 1:
                                             val_str = val_str.replace('-', '', val_str.count('-') - 1)
                                        amount = float(val_str)
                                        
                                        if amount == 0:
                                            continue
                                            
                                        currency = 'ARS'
                                        # If explicitly USD in text, treat as USD
                                        # OR if it's the second unique amount? Hard to say.
                                        # Let's trust "is_usd" flag for the line.
                                        if is_usd: 
                                            currency = 'USD'
                                        # Correction: If there is NO "USD" text, but there are 2 columns?
                                        # BBVA PDF usually doesn't say "USD" on every line, only in header.
                                        # BUT the regex `is_usd` checks the line.
                                        # In "STEAMGAMES... USD 14,99 ...", it works.
                                        # In normal ARS lines, it works.
                                        
                                        transactions.append({
                                            'date': date_obj,
                                            'description': description,
                                            'amount': amount,
                                            'currency': currency,
                                            'installments': installments,
                                            'category': 'Otros'
                                        })
                                    except:
                                        continue
    return transactions, text_content, detected_bank

def show_import_page():
    st.title("📤 Importar Resumen PDF")
    st.markdown("Cargá tu resumen de tarjeta (Visa/Mastercard/Amex) para extraer los gastos.")
    
    # File Uploader con estilo
    uploaded_file = st.file_uploader(
        "Arrastrá tu archivo aquí", 
        type=['pdf'], 
        help="Soporta resúmenes de BBVA, Galicia, etc."
    )
    
    if uploaded_file is not None:
        st.info(f"📄 Archivo cargado: {uploaded_file.name}")

        with st.spinner("Analizando documento..."):
            try:
                # Detectar banco
                bank_type = detect_bank_from_pdf(uploaded_file)
                uploaded_file.seek(0)  # Reset file pointer

                # Usar parser específico si está disponible
                if bank_type == 'GALICIA_VISA':
                    st.success("🎯 PDF de Galicia Visa detectado - Usando parser optimizado")
                    extracted_data, success = parse_galicia_pdf(uploaded_file, 'Visa')
                    detected_bank = 'Galicia Visa'
                    text_content = ""
                elif bank_type == 'GALICIA_AMEX':
                    st.success("🎯 PDF de Galicia Amex detectado - Usando parser optimizado")
                    extracted_data, success = parse_galicia_pdf(uploaded_file, 'Amex')
                    detected_bank = 'Galicia Amex'
                    text_content = ""
                else:
                    # Fallback al parser genérico
                    st.info("ℹ️ Usando parser genérico")
                    uploaded_file.seek(0)
                    extracted_data, text_content, detected_bank = parse_pdf_content(uploaded_file)

                if extracted_data:
                    df = pd.DataFrame(extracted_data)

                    st.success(f"✅ Se encontraron {len(df)} transacciones.")

                    # Bank Selection & Statement Period
                    st.markdown("### 🏦 Configuración del Resumen")

                    col1, col2 = st.columns(2)

                    with col1:
                        # Tus tarjetas
                        bank_options = [
                            'Galicia Visa',
                            'Galicia Amex',
                            'BBVA Visa'
                        ]
                        # Buscar index del banco detectado
                        default_index = 0
                        if detected_bank in bank_options:
                            default_index = bank_options.index(detected_bank)

                        selected_bank = st.selectbox(
                            "Banco / Tarjeta",
                            options=bank_options,
                            index=default_index,
                            help="Seleccioná tu tarjeta"
                        )

                    with col2:
                        # Selector de mes del resumen
                        current_date = datetime.now()
                        years = list(range(current_date.year, current_date.year - 5, -1))  # 5 años hacia atrás
                        months = [
                            ('Enero', 1), ('Febrero', 2), ('Marzo', 3), ('Abril', 4),
                            ('Mayo', 5), ('Junio', 6), ('Julio', 7), ('Agosto', 8),
                            ('Septiembre', 9), ('Octubre', 10), ('Noviembre', 11), ('Diciembre', 12)
                        ]

                        col_month, col_year = st.columns(2)
                        with col_month:
                            selected_month = st.selectbox(
                                "Mes del Resumen",
                                options=[m[0] for m in months],
                                index=current_date.month - 1,  # Default al mes actual
                                help="¿De qué mes es este resumen? (Ej: Diciembre para el resumen que pagás en diciembre)"
                            )
                        with col_year:
                            selected_year = st.selectbox(
                                "Año",
                                options=years,
                                index=0  # Default al año actual
                            )

                        # Construir statement_period
                        month_num = next(m[1] for m in months if m[0] == selected_month)
                        statement_period = f"{selected_year}-{month_num:02d}"

                        st.info(f"📅 Período del resumen: **{selected_month} {selected_year}**")

                    st.markdown("### 📝 Revisar y Confirmar")
                    st.markdown("Podés editar los datos antes de guardarlos. Verificá categorías y montos.")
                    
                    # Data Editor
                    edited_df = st.data_editor(
                        df,
                        use_container_width=True,
                        num_rows="dynamic",
                        column_config={
                            "amount": st.column_config.NumberColumn(
                                "Monto",
                                format="$ %.2f"
                            ),
                            "date": st.column_config.DateColumn(
                                "Fecha",
                                format="DD/MM/YYYY"
                            ),
                            "description": st.column_config.TextColumn(
                                "Descripción"
                            ),
                            "installments": st.column_config.TextColumn(
                                "Cuotas"
                            ),
                            "category": st.column_config.SelectboxColumn(
                                "Categoría",
                                options=[
                                    'Supermercado', 'Restaurante', 'Servicios', 
                                    'Transporte', 'Entretenimiento', 'Shopping', 
                                    'Suscripciones', 'Viajes', 'Otros'
                                ]
                            ),
                            "currency": st.column_config.SelectboxColumn(
                                "Moneda",
                                options=['ARS', 'USD'],
                                required=True
                            )
                        }
                    )
                    
                    col1, col2 = st.columns([1, 4])
                    with col1:
                        if st.button("💾 Guardar Transacciones", type="primary", use_container_width=True):
                            service = get_data_service()
                            cuotas_service = get_cuotas_service()
                            count = 0
                            transacciones_guardadas = []

                            for _, row in edited_df.iterrows():
                                data = row.to_dict()
                                data['bank'] = selected_bank
                                data['statement_period'] = statement_period  # Agregar período del resumen
                                if service.add_manual_transaction(data):
                                    count += 1
                                    transacciones_guardadas.append(data)

                            if count > 0:
                                # Procesar cuotas: propagar a meses futuros
                                cuotas_service.procesar_transacciones_importadas(
                                    transacciones_guardadas,
                                    statement_period
                                )

                                st.toast(f"✅ {count} transacciones guardadas en {selected_month} {selected_year}!", icon="🎉")
                                st.success("🔄 Cuotas propagadas automáticamente a meses futuros")
                                st.balloons()
                            else:
                                st.warning("No se guardaron nuevas transacciones (posibles duplicados).")
                            
                else:
                    st.warning("⚠️ No pudimos detectar transacciones automáticamente.")
                    st.markdown("El formato del PDF podría no ser compatible aún con nuestro parser genérico.")
                    
                    # Debug Area
                    with st.expander("🕵️ Versión Debug: Ver texto del PDF"):
                        st.text_area("Texto extraído (copiar para reportar issue):", value=text_content, height=300)
                        st.markdown("Si ves tus gastos aquí pero no en la tabla, es un problema de formato de fecha/monto.")
                    
            except Exception as e:
                st.error(f"Error al procesar el archivo: {e}")

if __name__ == "__main__":
    show_import_page()
