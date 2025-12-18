"""
Servicio para manejar la propagación inteligente de cuotas
"""
from datetime import datetime, date
from dateutil.relativedelta import relativedelta
from typing import List, Dict, Any
import pandas as pd
from services.local_storage import get_local_storage


class CuotasService:
    """Maneja la lógica de cuotas y su propagación a meses futuros."""

    def __init__(self):
        self.storage = get_local_storage()

    def parse_cuota(self, cuota_str: str) -> tuple:
        """
        Parsear string de cuota (ej: "3/12") -> (3, 12)
        Returns: (cuota_actual, cuota_total) o (None, None) si no es válido
        """
        if not cuota_str or cuota_str == '1/1':
            return None, None

        try:
            parts = cuota_str.split('/')
            if len(parts) == 2:
                actual = int(parts[0])
                total = int(parts[1])
                if total > 1:
                    return actual, total
        except:
            pass

        return None, None

    def propagar_cuotas_desde_transaccion(self, transaccion: Dict[str, Any], period: str):
        """
        Propagar una transacción con cuotas a los meses siguientes.

        Args:
            transaccion: Diccionario con la transacción original
            period: Período en formato "YYYY-MM" del resumen donde apareció
        """
        cuota_actual, cuota_total = self.parse_cuota(transaccion.get('installments', '1/1'))

        if cuota_actual is None or cuota_total is None:
            return  # No es una cuota válida

        # Calcular cuántas cuotas quedan por venir
        cuotas_restantes = cuota_total - cuota_actual

        if cuotas_restantes <= 0:
            return  # Ya es la última cuota

        # Obtener fecha del período
        year, month = map(int, period.split('-'))
        fecha_base = date(year, month, 1)

        # Propagar a los meses siguientes
        for i in range(1, cuotas_restantes + 1):
            # Calcular mes siguiente
            fecha_futura = fecha_base + relativedelta(months=i)
            periodo_futuro = f"{fecha_futura.year}-{fecha_futura.month:02d}"

            # Crear cuota propagada
            cuota_futura = {
                'original_id': transaccion.get('id'),
                'period': periodo_futuro,
                'date': transaccion.get('date'),
                'description': transaccion.get('description'),
                'amount': transaccion.get('amount'),
                'currency': transaccion.get('currency', 'ARS'),
                'category': transaccion.get('category', 'Otros'),
                'bank': transaccion.get('bank'),
                'installments': f"{cuota_actual + i}/{cuota_total}",
                'cuota_numero': cuota_actual + i,
                'cuota_total': cuota_total,
                'es_propagada': True,
                'encontrada_en_pdf': False
            }

            # Guardar en storage
            self.storage.save_cuota_propagada(cuota_futura)

    def procesar_transacciones_importadas(self, transacciones: List[Dict[str, Any]], period: str):
        """
        Procesar transacciones recién importadas de un PDF.

        1. Propagar cuotas a meses futuros
        2. Marcar cuotas propagadas que ahora aparecieron en el PDF real
        """
        for trans in transacciones:
            # Propagar cuotas futuras
            self.propagar_cuotas_desde_transaccion(trans, period)

            # Marcar si esta transacción era una cuota propagada
            if trans.get('id'):
                self.storage.marcar_cuota_como_real(trans['id'], period)

    def get_cuotas_para_periodo(self, period: str, incluir_encontradas: bool = False) -> List[Dict[str, Any]]:
        """
        Obtener cuotas para un período específico.

        Args:
            period: Período en formato "YYYY-MM"
            incluir_encontradas: Si False, excluye cuotas que ya fueron encontradas en PDFs reales

        Returns:
            Lista de cuotas para ese período
        """
        cuotas = self.storage.get_cuotas_por_periodo(period)

        if not incluir_encontradas:
            # Filtrar las que ya fueron encontradas en PDFs reales (para evitar duplicados)
            cuotas = [c for c in cuotas if not c.get('encontrada_en_pdf', False)]

        return cuotas

    def get_todas_las_cuotas_activas(self) -> pd.DataFrame:
        """
        Obtener todas las cuotas propagadas que aún no fueron pagadas.
        Útil para ver el compromiso total de cuotas futuras.
        """
        todas_cuotas = self.storage.load_cuotas_propagadas()

        # Filtrar solo las que no fueron encontradas en PDFs (aún son proyecciones)
        cuotas_pendientes = [c for c in todas_cuotas if not c.get('encontrada_en_pdf', False)]

        if not cuotas_pendientes:
            return pd.DataFrame()

        return pd.DataFrame(cuotas_pendientes)


# Singleton
_service = None

def get_cuotas_service() -> CuotasService:
    """Obtener instancia del servicio de cuotas."""
    global _service
    if _service is None:
        _service = CuotasService()
    return _service
