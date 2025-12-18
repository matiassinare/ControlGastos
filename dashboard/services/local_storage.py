"""
Sistema de persistencia local para datos del dashboard
"""
import json
from pathlib import Path
from datetime import datetime, date
import pandas as pd
from typing import Dict, List, Any


class LocalStorage:
    """Maneja la persistencia local de datos."""

    def __init__(self):
        self.data_dir = Path(__file__).parent.parent / 'data'
        self.data_dir.mkdir(exist_ok=True)

        self.sueldos_file = self.data_dir / 'sueldos.json'
        self.gastos_manuales_file = self.data_dir / 'gastos_manuales.json'
        self.cuotas_file = self.data_dir / 'cuotas_propagadas.json'

    def _serialize_date(self, obj):
        """Serializar fechas para JSON."""
        if isinstance(obj, (datetime, date)):
            return obj.isoformat()
        raise TypeError(f"Type {type(obj)} not serializable")

    def _deserialize_date(self, date_str: str):
        """Deserializar fechas desde JSON."""
        try:
            return datetime.fromisoformat(date_str).date()
        except:
            return date_str

    # --- SUELDOS ---
    def save_sueldo(self, period: str, amount: float):
        """Guardar sueldo de un período."""
        sueldos = self.load_sueldos()
        sueldos[period] = amount

        with open(self.sueldos_file, 'w') as f:
            json.dump(sueldos, f, indent=2)

    def load_sueldos(self) -> Dict[str, float]:
        """Cargar todos los sueldos guardados."""
        if self.sueldos_file.exists():
            with open(self.sueldos_file, 'r') as f:
                return json.load(f)
        return {}

    def get_sueldo_vigente(self, period: str) -> float:
        """
        Obtener el sueldo vigente para un período.
        Si no hay sueldo específico para ese período, busca el último sueldo anterior.

        Args:
            period: Período en formato "YYYY-MM"

        Returns:
            Sueldo vigente o 0 si no hay ninguno
        """
        sueldos = self.load_sueldos()

        # Si hay sueldo exacto para este período
        if period in sueldos:
            return sueldos[period]

        # Buscar el último sueldo anterior
        all_periods = sorted(sueldos.keys(), reverse=True)
        for p in all_periods:
            if p < period:  # Comparación de strings YYYY-MM funciona correctamente
                return sueldos[p]

        return 0.0

    # --- GASTOS MANUALES ---
    def save_gasto_manual(self, gasto: Dict[str, Any]):
        """Agregar un gasto manual."""
        gastos = self.load_gastos_manuales()
        gastos.append(gasto)

        with open(self.gastos_manuales_file, 'w') as f:
            json.dump(gastos, f, indent=2, default=self._serialize_date)

    def load_gastos_manuales(self) -> List[Dict[str, Any]]:
        """Cargar todos los gastos manuales."""
        if self.gastos_manuales_file.exists():
            with open(self.gastos_manuales_file, 'r') as f:
                gastos = json.load(f)
                # Deserializar fechas
                for g in gastos:
                    if 'date' in g:
                        g['date'] = self._deserialize_date(g['date'])
                return gastos
        return []

    def update_gasto_manual(self, gasto_id: str, updates: Dict[str, Any]):
        """Actualizar un gasto manual (ej: marcar como pagado)."""
        gastos = self.load_gastos_manuales()

        for gasto in gastos:
            if gasto['id'] == gasto_id:
                gasto.update(updates)
                break

        with open(self.gastos_manuales_file, 'w') as f:
            json.dump(gastos, f, indent=2, default=self._serialize_date)

    # --- MESES OCULTOS ---
    def save_meses_ocultos(self, meses: set):
        """Guardar set de meses ocultos."""
        config_file = self.data_dir / 'config_dashboard.json'
        # Cargar config existente
        config = {}
        if config_file.exists():
            with open(config_file, 'r') as f:
                try:
                    config = json.load(f)
                except:
                    pass

        config['meses_ocultos'] = list(meses)

        with open(config_file, 'w') as f:
            json.dump(config, f, indent=2)

    def load_meses_ocultos(self) -> set:
        """Cargar set de meses ocultos."""
        config_file = self.data_dir / 'config_dashboard.json'
        if config_file.exists():
            with open(config_file, 'r') as f:
                try:
                    config = json.load(f)
                    return set(config.get('meses_ocultos', []))
                except:
                    pass
        return set()

    # --- CUOTAS PROPAGADAS ---
    def save_cuota_propagada(self, cuota: Dict[str, Any]):
        """Guardar una cuota propagada a un período futuro."""
        cuotas = self.load_cuotas_propagadas()

        # Verificar que no exista duplicada
        key = f"{cuota['original_id']}_{cuota['period']}"
        if not any(c.get('key') == key for c in cuotas):
            cuota['key'] = key
            cuotas.append(cuota)

            with open(self.cuotas_file, 'w') as f:
                json.dump(cuotas, f, indent=2, default=self._serialize_date)

    def load_cuotas_propagadas(self) -> List[Dict[str, Any]]:
        """Cargar cuotas propagadas."""
        if self.cuotas_file.exists():
            with open(self.cuotas_file, 'r') as f:
                cuotas = json.load(f)
                # Deserializar fechas
                for c in cuotas:
                    if 'date' in c:
                        c['date'] = self._deserialize_date(c['date'])
                return cuotas
        return []

    def get_cuotas_por_periodo(self, period: str) -> List[Dict[str, Any]]:
        """Obtener cuotas de un período específico."""
        cuotas = self.load_cuotas_propagadas()
        return [c for c in cuotas if c['period'] == period]

    def marcar_cuota_como_real(self, original_id: str, period: str):
        """
        Marcar que una cuota propagada ya fue detectada en un PDF real.
        Esto evita duplicados cuando importamos el PDF del mes.
        """
        cuotas = self.load_cuotas_propagadas()
        key = f"{original_id}_{period}"

        for cuota in cuotas:
            if cuota.get('key') == key:
                cuota['encontrada_en_pdf'] = True
                break

        with open(self.cuotas_file, 'w') as f:
            json.dump(cuotas, f, indent=2, default=self._serialize_date)

    def update_cuota_propagada(self, original_id: str, period: str, updates: Dict[str, Any]):
        """
        Actualizar una cuota propagada (ej: agregar nota).
        Identificamos la cuota por original_id + period.
        """
        cuotas = self.load_cuotas_propagadas()
        key = f"{original_id}_{period}"
        found = False

        for cuota in cuotas:
            # Chequear por key o por id+period
            if cuota.get('key') == key or (cuota.get('original_id') == original_id and cuota.get('period') == period):
                cuota.update(updates)
                found = True
                break

        if found:
            with open(self.cuotas_file, 'w') as f:
                json.dump(cuotas, f, indent=2, default=self._serialize_date)
            return True
        return False

    def delete_cuota_propagada(self, original_id: str, period: str) -> bool:
        """
        Eliminar una cuota propagada específica (ej: anular solo esta cuota).
        """
        cuotas = self.load_cuotas_propagadas()
        key = f"{original_id}_{period}"
        initial_len = len(cuotas)

        # Filtrar la cuota que coincida
        cuotas = [c for c in cuotas if not (c.get('key') == key or (c.get('original_id') == original_id and c.get('period') == period))]

        if len(cuotas) < initial_len:
            with open(self.cuotas_file, 'w') as f:
                json.dump(cuotas, f, indent=2, default=self._serialize_date)
            return True
        return False


# Singleton
_storage = None

def get_local_storage() -> LocalStorage:
    """Obtener instancia de LocalStorage."""
    global _storage
    if _storage is None:
        _storage = LocalStorage()
    return _storage
