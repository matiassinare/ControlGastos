"""
Galicia Scraper
Scraper específico para Galicia Visa y Amex
"""

import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import time
import os
from typing import List, Dict
from datetime import datetime, timedelta
from playwright.sync_api import Page
from banks.galicia_pdf_parser import GaliciaPDFParser
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()


class GaliciaScraper:
    """Scraper para Galicia Visa y Amex."""

    def __init__(self, page: Page, verbose: bool = False, download_dir: Path = None):
        """
        Inicializar scraper de Galicia.

        Args:
            page: Página de Playwright
            verbose: Si True, muestra logs detallados
            download_dir: Directorio para descargar PDFs
        """
        self.page = page
        self.verbose = verbose
        self.download_dir = download_dir or Path(__file__).parent.parent / 'downloads'
        self.download_dir.mkdir(exist_ok=True)

    def log(self, message: str):
        """Imprimir log si verbose está activado."""
        if self.verbose:
            print(f"[GALICIA] {message}")

    def scrape(self) -> List[Dict]:
        """
        Scrapear transacciones de Galicia Visa y Amex descargando PDFs.

        Returns:
            List[Dict]: Lista de transacciones
        """
        try:
            # Hacer login automático
            if not self._login():
                print("❌ Error en login. Verificá las credenciales en .env")
                return []

            self.log("✓ Login exitoso")

            # Descargar PDFs de ambas tarjetas
            all_transactions = []

            # Tarjeta 0 (probablemente Visa)
            self.log("Descargando resumen de tarjeta 0...")
            pdf_path_0 = self._download_card_pdf(card_index=0)
            if pdf_path_0:
                self.log(f"PDF descargado: {pdf_path_0}")
                self.log("Parseando transacciones de Visa...")
                transactions_0 = self._parse_pdf(pdf_path_0, 'Visa')
                all_transactions.extend(transactions_0)
                self.log(f"Encontradas {len(transactions_0)} transacciones de Visa")

            # Volver a inicio para la segunda tarjeta
            self.page.get_by_role("link", name="Inicio").click()
            self.page.wait_for_timeout(2000)

            # Tarjeta 1 (probablemente Amex)
            self.log("Descargando resumen de tarjeta 1...")
            pdf_path_1 = self._download_card_pdf(card_index=1)
            if pdf_path_1:
                self.log(f"PDF descargado: {pdf_path_1}")
                self.log("Parseando transacciones de Amex...")
                transactions_1 = self._parse_pdf(pdf_path_1, 'Amex')
                all_transactions.extend(transactions_1)
                self.log(f"Encontradas {len(transactions_1)} transacciones de Amex")

            self.log(f"✓ Encontradas {len(all_transactions)} transacciones")

            return all_transactions

        except Exception as e:
            self.log(f"❌ Error durante scraping: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return []

    def _login(self) -> bool:
        """
        Hacer login automático en Galicia.

        Returns:
            bool: True si el login fue exitoso, False si falló
        """
        try:
            # Obtener credenciales del .env
            dni = os.getenv('GALICIA_DNI')
            username = os.getenv('GALICIA_USERNAME')
            password = os.getenv('GALICIA_PASSWORD')

            if not dni or not username or not password:
                print("❌ Credenciales de Galicia no configuradas en .env")
                print("Configurá: GALICIA_DNI, GALICIA_USERNAME, GALICIA_PASSWORD")
                return False

            self.log("Navegando a login de Galicia...")
            self.page.goto('https://onlinebanking.bancogalicia.com.ar/login', timeout=30000)

            # Esperar a que cargue la página
            self.page.wait_for_load_state('networkidle')

            # Ingresar DNI
            self.log(f"Ingresando DNI: {dni}")
            dni_input = self.page.get_by_role("spinbutton", name="Tu DNI")
            dni_input.click()
            dni_input.fill(dni)
            self.page.wait_for_timeout(800)

            # Ingresar usuario
            self.log("Ingresando usuario...")
            user_input = self.page.get_by_role("textbox", name="Tu usuario Galicia")
            user_input.click()
            user_input.fill(username)
            self.page.wait_for_timeout(800)

            # Ingresar clave
            self.log("Ingresando clave...")
            pass_input = self.page.get_by_role("textbox", name="Tu clave Galicia")
            pass_input.click()
            pass_input.fill(password)
            self.page.wait_for_timeout(800)

            # Esperar a que el botón se habilite y hacer click
            self.log("Esperando a que el botón se habilite...")
            submit_button = self.page.get_by_role("button", name="iniciar sesión")

            # Esperar hasta 10 segundos a que el botón esté enabled
            for _ in range(20):
                if not submit_button.is_disabled():
                    break
                self.page.wait_for_timeout(500)

            # Click en "iniciar sesión"
            self.log("Haciendo click en iniciar sesión...")
            submit_button.click()

            # Esperar a que cargue
            self.log("Esperando que cargue el dashboard...")
            self.page.wait_for_timeout(5000)

            # Verificar que estemos logueados (no en login)
            if "login" in self.page.url.lower():
                self.log("❌ Seguimos en login, credenciales incorrectas")
                if self.verbose:
                    screenshot_path = self.download_dir / f"debug_galicia_login_failed_{int(time.time())}.png"
                    self.page.screenshot(path=str(screenshot_path))
                    print(f"Screenshot guardado: {screenshot_path}")
                return False

            self.log(f"Login exitoso. URL actual: {self.page.url}")
            return True

        except Exception as e:
            self.log(f"❌ Error durante login: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return False

    def _parse_pdf(self, pdf_path: Path, card_type: str) -> List[Dict]:
        """
        Parsear PDF de resumen y extraer transacciones.

        Args:
            pdf_path: Path al archivo PDF
            card_type: Tipo de tarjeta ('Visa' o 'Amex')

        Returns:
            Lista de transacciones
        """
        try:
            parser = GaliciaPDFParser(str(pdf_path))
            transactions = parser.parse(card_type)
            return transactions
        except Exception as e:
            self.log(f"Error parseando PDF: {e}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return []

    def _download_card_pdf(self, card_index: int) -> Path | None:
        """
        Descargar PDF de resumen de una tarjeta específica.

        Args:
            card_index: Índice de la tarjeta (0 o 1)

        Returns:
            Path al PDF descargado o None si falló
        """
        try:
            # Click en la tarjeta
            self.log(f"Haciendo click en tarjeta {card_index}...")
            self.page.locator(f"#tarjeta-{card_index} > div:nth-child(3)").click()
            self.page.wait_for_timeout(1500)

            # Click en "Resumen"
            self.log("Navegando a Resumen...")
            self.page.locator("button").filter(has_text="Resumen").click()
            self.page.wait_for_timeout(1500)

            # Click en "Mostrar último resumen" y esperar el popup
            self.log("Descargando último resumen...")

            # Capturar el popup que se abre con el PDF
            with self.page.expect_popup() as popup_info:
                self.page.locator("button").filter(has_text="Mostrar último resumen").click()

            popup = popup_info.value
            self.page.wait_for_timeout(3000)

            # El popup contiene el PDF renderizado como blob
            # Necesitamos usar PDF printing de Playwright
            self.log("Generando PDF desde popup...")

            # Generar nombre único para el PDF
            timestamp = int(time.time())
            card_name = "visa" if card_index == 0 else "amex"
            pdf_filename = f"galicia_{card_name}_{timestamp}.pdf"
            pdf_path = self.download_dir / pdf_filename

            # Usar print_to_pdf de Playwright para capturar el contenido
            popup.pdf(
                path=str(pdf_path),
                format='A4',
                print_background=True
            )

            # Cerrar el popup
            popup.close()

            self.log(f"✓ PDF guardado: {pdf_path}")
            return pdf_path

        except Exception as e:
            self.log(f"❌ Error descargando PDF de tarjeta {card_index}: {str(e)}")
            if self.verbose:
                import traceback
                traceback.print_exc()
            return None
