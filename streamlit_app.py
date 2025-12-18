"""
Expense Tracker - Aplicación principal
Punto de entrada para Streamlit Cloud
"""

# Redirigir al dashboard principal
import sys
from pathlib import Path

# Agregar el directorio dashboard al path
dashboard_path = Path(__file__).parent / "dashboard"
sys.path.insert(0, str(dashboard_path))

# Importar y ejecutar la página de resumen
from pages import show_dashboard

if __name__ == "__main__":
    # Ejecutar la aplicación principal
    exec(open(dashboard_path / "pages" / "1_📊_Resumen.py").read())
