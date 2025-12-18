"""
Galicia PDF Parser
Parser para extraer transacciones de PDFs de resumen de Galicia Visa/Amex
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import re
import pdfplumber
from typing import List, Dict
from datetime import datetime


class GaliciaPDFParser:
    """Parser para PDFs de resumen de Galicia."""

    def __init__(self, pdf_path: str):
        """
        Inicializar parser.

        Args:
            pdf_path: Ruta al archivo PDF
        """
        self.pdf_path = pdf_path

    def parse(self, card_type: str = 'Visa') -> List[Dict]:
        """
        Parsear PDF y extraer transacciones.

        Args:
            card_type: Tipo de tarjeta ('Visa' o 'Amex')

        Returns:
            List[Dict]: Lista de transacciones
        """
        transactions = []

        with pdfplumber.open(self.pdf_path) as pdf:
            # Buscar en todas las páginas
            for page_num, page in enumerate(pdf.pages, 1):
                text = page.extract_text()

                if not text:
                    continue

                # Buscar sección "DETALLE DEL CONSUMO"
                if 'DETALLE DEL CONSUMO' in text:
                    page_transactions = self._extract_transactions_from_page(text, card_type)
                    transactions.extend(page_transactions)

        return transactions

    def _extract_transactions_from_page(self, text: str, card_type: str) -> List[Dict]:
        """
        Extraer transacciones de una página.

        Args:
            text: Texto de la página
            card_type: Tipo de tarjeta

        Returns:
            List[Dict]: Transacciones encontradas
        """
        transactions = []
        lines = text.split('\n')

        # Encontrar inicio de "DETALLE DEL CONSUMO"
        in_transactions = False
        current_tarjeta = None

        for i, line in enumerate(lines):
            # Detectar inicio de sección
            if 'DETALLE DEL CONSUMO' in line:
                in_transactions = True
                continue

            # Detectar fin de sección
            if in_transactions and ('TOTAL A PAGAR' in line or 'Plan V:' in line):
                break

            # Detectar qué tarjeta estamos procesando
            if 'TARJETA' in line and 'Total Consumos' in line:
                # Línea como: "TARJETA 3769 Total Consumos de MATIAS IGNAC SINARE"
                current_tarjeta = line.split()[1] if len(line.split()) > 1 else None
                continue

            if not in_transactions:
                continue

            # Parsear línea de transacción
            # Formato: FECHA REFERENCIA [CUOTA] COMPROBANTE PESOS [DÓLARES]
            # Ejemplo: "31-08-25 * MERPAGO*MERCADOLIBRE 03/03 886717 49.999,66"
            # Ejemplo: "08-11-25 APPLE.COM/BILL USD 20,00 957806 20,00"

            # Regex para detectar líneas de transacciones
            # Debe empezar con fecha DD-MM-YY
            date_pattern = r'^(\d{2}-\d{2}-\d{2})\s+'
            match = re.match(date_pattern, line)

            if match:
                # Ignorar líneas de impuestos y cargos del banco
                if any(keyword in line.upper() for keyword in [
                    'IMPUESTO DE SELLOS',
                    'IIBB PERCEP',
                    'IVA RG',
                    'DB.RG',
                    'SU PAGO'
                ]):
                    continue

                transaction = self._parse_transaction_line(line, card_type, current_tarjeta)
                if transaction:
                    transactions.append(transaction)

        return transactions

    def _parse_transaction_line(self, line: str, card_type: str, tarjeta_num: str) -> Dict | None:
        """
        Parsear una línea de transacción.

        Args:
            line: Línea de texto
            card_type: Tipo de tarjeta
            tarjeta_num: Número de tarjeta (últimos 4 dígitos)

        Returns:
            Dict con la transacción o None si no se pudo parsear
        """
        try:
            # Patrones para detectar diferentes formatos
            # Formato 1: DD-MM-YY [*|K] DESCRIPCION [CUOTA] COMPROBANTE MONTO_PESOS [MONTO_USD]
            # Ejemplo: "31-08-25 * MERPAGO*MERCADOLIBRE 03/03 886717 49.999,66"
            # Ejemplo: "08-11-25 APPLE.COM/BILL USD 20,00 957806 20,00"
            # Ejemplo: "02-11-25 K VIA COSENZA-COSENZA GELA 965290 12.800,00"

            parts = line.split()

            if len(parts) < 3:
                return None

            # Fecha (primer elemento)
            date_str = parts[0]
            date = self.parse_date(date_str)

            # El resto es descripción + cuota + comprobante + montos
            remaining = ' '.join(parts[1:])

            # Detectar si tiene USD en la descripción
            has_usd = 'USD' in remaining.upper()

            # Buscar montos al final (pueden ser pesos y/o dólares)
            # Formato de monto: 12.800,00 o 49.999,66 o 20,00
            money_pattern = r'(\d{1,3}(?:\.\d{3})*,\d{2})'
            montos = re.findall(money_pattern, remaining)

            if not montos:
                return None

            # Determinar moneda y monto
            # Si tiene USD en descripción, el último monto es USD, el penúltimo es ARS (si existe)
            # Si no tiene USD, todos los montos son ARS

            if has_usd and len(montos) >= 1:
                # Transacción en USD
                amount_usd = self.parse_amount(montos[-1])
                currency = 'USD'
                amount = amount_usd
            else:
                # Transacción en ARS
                amount_ars = self.parse_amount(montos[-1])
                currency = 'ARS'
                amount = amount_ars

            # Extraer descripción (todo entre el símbolo inicial y antes de los números finales)
            # Remover fecha
            desc_start = len(parts[0]) + 1

            # Remover indicador * o K si existe
            if len(parts) > 1 and parts[1] in ['*', 'K']:
                desc_start += len(parts[1]) + 1

            # Encontrar dónde termina la descripción (antes de los números al final)
            # Buscar el último grupo de números (comprobante + montos)
            numbers_pattern = r'\s+\d+\s+' + money_pattern
            numbers_match = re.search(numbers_pattern, remaining)

            if numbers_match:
                desc_end = numbers_match.start()
                description = remaining[:desc_end].strip()
            else:
                description = remaining.strip()

            # Limpiar descripción de USD y otros artefactos
            # Remover "USD XX,XX" del medio de la descripción
            description = re.sub(r'\s+USD\s+[\d,\.]+', '', description)
            # Remover indicadores K y * del inicio
            description = re.sub(r'^\s*[K\*]\s+', '', description)
            description = description.strip()

            # Detectar cuota (formato XX/XX)
            cuota = None
            cuota_match = re.search(r'(\d{2}/\d{2})', description)
            if cuota_match:
                cuota = cuota_match.group(1)
                # Remover cuota de la descripción
                description = description.replace(cuota, '').strip()

            # Nombre de tarjeta
            card_name = f"{card_type} Galicia"
            if tarjeta_num:
                card_name += f" ({tarjeta_num})"

            return {
                'bank': 'Galicia',
                'card_type': card_type,
                'card_name': card_name,
                'date': date,
                'description': description,
                'amount': amount,
                'currency': currency,
                'cuota': cuota,
                'is_manual': False,
                'category': None,
                'notes': None
            }

        except Exception as e:
            print(f"Error parseando línea: {line}")
            print(f"Error: {e}")
            return None

    def parse_date(self, date_str: str) -> str:
        """
        Parsear fecha en formato 'DD-MM-YY' (e.g., '31-08-25').

        Args:
            date_str: Fecha como string

        Returns:
            Fecha en formato YYYY-MM-DD
        """
        try:
            # Formato: DD-MM-YY
            day, month, year = date_str.split('-')

            # Convertir año de 2 dígitos a 4 dígitos
            # Asumimos que 00-49 es 2000-2049, y 50-99 es 1950-1999
            year_int = int(year)
            if year_int >= 50:
                full_year = 1900 + year_int
            else:
                full_year = 2000 + year_int

            return f"{full_year}-{month}-{day}"

        except Exception as e:
            print(f"Error parseando fecha '{date_str}': {e}")
            return date_str

    def parse_amount(self, amount_str: str) -> float:
        """
        Parsear monto en formato argentino (e.g., '49.999,66').

        Args:
            amount_str: Monto como string

        Returns:
            Monto como float
        """
        try:
            # Remover puntos (separador de miles)
            amount_str = amount_str.replace('.', '')
            # Reemplazar coma (separador decimal) por punto
            amount_str = amount_str.replace(',', '.')
            return float(amount_str)
        except Exception as e:
            print(f"Error parseando monto '{amount_str}': {e}")
            return 0.0


if __name__ == '__main__':
    # Test del parser
    if len(sys.argv) > 1:
        pdf_path = sys.argv[1]
        card_type = sys.argv[2] if len(sys.argv) > 2 else 'Visa'

        print(f"\nParseando PDF de Galicia {card_type}: {pdf_path}\n")

        parser = GaliciaPDFParser(pdf_path)
        transactions = parser.parse(card_type)

        print(f"Encontradas {len(transactions)} transacciones:\n")

        for t in transactions:
            cuota_str = f" [{t['cuota']}]" if t['cuota'] else ""
            print(f"  {t['date']} - {t['description']}{cuota_str}: {t['currency']} {t['amount']:.2f}")

    else:
        print("Uso: python galicia_pdf_parser.py <ruta_al_pdf> [Visa|Amex]")
