"""
BBVA PDF Parser
Parsea el PDF del resumen de tarjeta BBVA
"""

import re
import pdfplumber
from datetime import datetime
from typing import List, Dict
import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

from utils import parse_amount, parse_cuota, clean_description, detect_currency


class BBVAPDFParser:
    """Parser para PDFs de resumen BBVA."""

    def __init__(self, pdf_path: str):
        """
        Inicializar parser.

        Args:
            pdf_path: Ruta al PDF
        """
        self.pdf_path = pdf_path

    def parse_date(self, date_str: str) -> str:
        """
        Parsear fecha en formato BBVA.

        Args:
            date_str: Fecha en formato 'DD-MMM-YY' (ej: '13-Mar-25')

        Returns:
            str: Fecha en formato 'YYYY-MM-DD'
        """
        # Mapeo de meses en español
        meses = {
            'Ene': '01', 'Feb': '02', 'Mar': '03', 'Abr': '04',
            'May': '05', 'Jun': '06', 'Jul': '07', 'Ago': '08',
            'Sep': '09', 'Oct': '10', 'Nov': '11', 'Dic': '12'
        }

        try:
            # Formato: 13-Mar-25
            parts = date_str.split('-')
            day = parts[0].zfill(2)
            month = meses.get(parts[1], '01')
            year = f"20{parts[2]}"  # Asumimos siglo 21

            return f"{year}-{month}-{day}"
        except Exception as e:
            print(f"Warning: No se pudo parsear fecha '{date_str}': {e}")
            return datetime.now().strftime('%Y-%m-%d')

    def extract_cuota_from_description(self, description: str) -> str:
        """
        Extraer información de cuota de la descripción.

        Args:
            description: Descripción (ej: 'COPPEL C.09/12')

        Returns:
            str: Formato '9/12' o None
        """
        # Buscar patrón C.XX/YY
        match = re.search(r'C\.(\d+)/(\d+)', description)
        if match:
            current = match.group(1)
            total = match.group(2)
            return f"{current}/{total}"
        return None

    def parse_transactions(self) -> List[Dict]:
        """
        Parsear todas las transacciones del PDF.

        Returns:
            List[Dict]: Lista de transacciones
        """
        transactions = []

        with pdfplumber.open(self.pdf_path) as pdf:
            # Las transacciones están en la página 2 (índice 1)
            if len(pdf.pages) < 2:
                print("Warning: PDF no tiene suficientes páginas")
                return transactions

            page = pdf.pages[1]  # Página 2
            text = page.extract_text()

            # Buscar sección "Consumos Matias I Sinare"
            # o el nombre que corresponda
            lines = text.split('\n')

            in_consumos_section = False
            in_own_consumos = False

            for i, line in enumerate(lines):
                # Detectar inicio de sección de consumos propios
                if 'Consumos Matias' in line or 'CONSUMOS DE MATIAS' in line:
                    in_consumos_section = True
                    in_own_consumos = True
                    continue

                # Detectar fin de consumos propios
                if 'TOTAL CONSUMOS DE' in line and in_own_consumos:
                    in_own_consumos = False
                    continue

                # Detectar inicio de consumos de otros titulares (omitir)
                if 'Consumos' in line and 'Ariana' in line:
                    in_consumos_section = False
                    continue

                # Solo parsear líneas de transacciones propias
                if not in_consumos_section or not in_own_consumos:
                    continue

                # Parsear línea de transacción
                # Formato esperado: DD-MMM-YY DESCRIPCION NRO_CUPON MONTO [MONTO_USD]
                # Ejemplo: 13-Mar-25 COPPEL C.09/12 009904 91.666,58

                # Patrón: fecha al inicio (DD-MMM-YY)
                if re.match(r'\d{2}-[A-Za-z]{3}-\d{2}', line):
                    parts = line.split()

                    if len(parts) < 4:
                        continue

                    # Fecha (primera parte)
                    fecha = parts[0]

                    # Buscar monto en pesos (penúltimo o último elemento)
                    # El monto tiene formato: 12.345,67 o 345,67
                    monto_pesos = None
                    monto_usd = None
                    nro_cupon = None
                    descripcion_parts = []

                    # Iterar desde el final para encontrar montos
                    for j in range(len(parts) - 1, 0, -1):
                        part = parts[j]

                        # Detectar si es un monto (contiene coma decimal)
                        if ',' in part and re.match(r'[\d\.,]+', part):
                            if monto_pesos is None:
                                monto_pesos = part
                            elif monto_usd is None:
                                # Podría ser monto en USD (si hay dos montos)
                                monto_usd = monto_pesos
                                monto_pesos = part
                            continue

                        # Detectar nro de cupón (6 dígitos numéricos)
                        if re.match(r'\d{6}', part) and nro_cupon is None:
                            nro_cupon = part
                            continue

                        # El resto es descripción
                        descripcion_parts.insert(0, part)

                    if not monto_pesos:
                        continue

                    # Reconstruir descripción (todo entre fecha y número de cupón)
                    descripcion = ' '.join(descripcion_parts[1:])  # Omitir fecha

                    # Parsear
                    date_parsed = self.parse_date(fecha)
                    amount = parse_amount(monto_pesos)
                    cuota = self.extract_cuota_from_description(descripcion)
                    currency = 'USD' if monto_usd else 'ARS'

                    # Si hay monto en USD, usarlo
                    if monto_usd and 'USD' in descripcion:
                        amount = parse_amount(monto_usd)

                    transaction = {
                        'bank': 'BBVA',
                        'card_type': 'Visa',
                        'card_name': 'Visa BBVA',
                        'date': date_parsed,
                        'description': clean_description(descripcion),
                        'amount': abs(amount),  # Siempre positivo
                        'currency': currency,
                        'cuota': cuota,
                        'is_manual': False,
                        'category': None,
                        'notes': None
                    }

                    transactions.append(transaction)

        return transactions


def test_parser():
    """Test del parser con el PDF de ejemplo."""
    import sys

    if len(sys.argv) < 2:
        print("Uso: python bbva_pdf_parser.py <ruta_al_pdf>")
        sys.exit(1)

    pdf_path = sys.argv[1]
    parser = BBVAPDFParser(pdf_path)
    transactions = parser.parse_transactions()

    print(f"\n✅ Encontradas {len(transactions)} transacciones:\n")

    for t in transactions:
        cuota_str = f" [{t['cuota']}]" if t['cuota'] else ""
        print(f"{t['date']} | {t['description']:40s} | ${t['amount']:>10,.2f} {t['currency']}{cuota_str}")


if __name__ == '__main__':
    test_parser()
