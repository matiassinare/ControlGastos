"""
Credit Card Scraper - Clase Principal
Coordina el scraping de múltiples bancos y guarda en Supabase
"""

import os
import json
from pathlib import Path
from typing import List, Dict, Optional
from dotenv import load_dotenv
from supabase import create_client, Client
from playwright.sync_api import sync_playwright, Browser, BrowserContext

# Cargar variables de entorno
load_dotenv()


class CreditCardScraper:
    """Scraper principal para tarjetas de crédito."""

    def __init__(self, verbose: bool = False):
        """
        Inicializar scraper.

        Args:
            verbose: Si True, muestra logs detallados
        """
        self.verbose = verbose
        self.cookies_dir = Path(__file__).parent / '.cookies'
        self.cookies_dir.mkdir(exist_ok=True)
        self.download_dir = Path(__file__).parent / 'downloads'
        self.download_dir.mkdir(exist_ok=True)

        # Cliente Supabase
        supabase_url = os.getenv('SUPABASE_URL')
        supabase_key = os.getenv('SUPABASE_KEY')

        if not supabase_url or not supabase_key:
            raise ValueError("Faltan credenciales de Supabase en .env")

        self.supabase: Client = create_client(supabase_url, supabase_key)
        self.log("✅ Conectado a Supabase")

    def log(self, message: str):
        """Imprimir log si verbose está activado."""
        if self.verbose:
            print(f"[DEBUG] {message}")

    def scrape_galicia(self) -> List[Dict]:
        """
        Scrapear Galicia (Visa + Amex).

        Returns:
            List[Dict]: Lista de transacciones
        """
        print("\n💳 Scrapeando Galicia (Visa + Amex)...")

        from banks.galicia import GaliciaScraper

        with sync_playwright() as p:
            browser = p.chromium.launch(headless=not self.verbose)
            context = browser.new_context(
                permissions=[],  # Denegar geolocalización y otros permisos
                geolocation=None
            )

            page = context.new_page()
            scraper = GaliciaScraper(page, self.verbose, self.download_dir)

            try:
                transactions = scraper.scrape()
                browser.close()
                return transactions
            except Exception as e:
                print(f"❌ Error scrapeando Galicia: {e}")
                if self.verbose:
                    import traceback
                    traceback.print_exc()
                browser.close()
                return []

    def scrape_bbva(self) -> List[Dict]:
        """
        Scrapear BBVA Visa.

        Returns:
            List[Dict]: Lista de transacciones
        """
        print("\n💳 Scrapeando BBVA Visa...")

        # TODO: Implementar scraper de BBVA similar a Galicia
        print("⚠️  BBVA scraper no implementado todavía")
        return []

    def save_to_supabase(self, transactions: List[Dict]) -> Dict[str, int]:
        """
        Guardar transacciones en Supabase.

        Args:
            transactions: Lista de transacciones

        Returns:
            Dict con estadísticas (inserted, duplicates)
        """
        inserted = 0
        duplicates = 0

        for transaction in transactions:
            try:
                self.supabase.table('transactions').insert(transaction).execute()
                inserted += 1
                self.log(f"✓ Insertada: {transaction['description']} - ${transaction['amount']}")
            except Exception as e:
                # Si es error de unique constraint, es duplicado
                if 'unique' in str(e).lower() or 'duplicate' in str(e).lower():
                    duplicates += 1
                    self.log(f"⊗ Duplicado: {transaction['description']}")
                else:
                    print(f"⚠️  Error insertando transacción: {e}")

        return {'inserted': inserted, 'duplicates': duplicates}

    def scrape_all(self, bank_filter: Optional[str] = None) -> Dict[str, Dict]:
        """
        Scrapear todos los bancos.

        Args:
            bank_filter: 'bbva', 'galicia' o None para todos

        Returns:
            Dict con resultados por banco
        """
        results = {}

        # Determinar qué bancos scrapear
        banks = []
        if bank_filter:
            banks = [bank_filter.lower()]
        else:
            banks = ['galicia', 'bbva']

        # Scrapear cada banco
        for bank in banks:
            try:
                if bank == 'galicia':
                    transactions = self.scrape_galicia()
                    stats = self.save_to_supabase(transactions)
                    results['Galicia (Visa + Amex)'] = {
                        'found': len(transactions),
                        'inserted': stats['inserted'],
                        'duplicates': stats['duplicates']
                    }

                elif bank == 'bbva':
                    transactions = self.scrape_bbva()
                    stats = self.save_to_supabase(transactions)
                    results['BBVA Visa'] = {
                        'found': len(transactions),
                        'inserted': stats['inserted'],
                        'duplicates': stats['duplicates']
                    }

            except Exception as e:
                print(f"\n❌ Error con {bank}: {e}")
                results[bank] = {
                    'found': 0,
                    'inserted': 0,
                    'duplicates': 0
                }

        return results

    def export_galicia_cookies(self):
        """Exportar cookies de Galicia (no usado con login automático)."""
        print("⚠️  Este método ya no es necesario con login automático por credenciales")

    def export_bbva_cookies(self):
        """Exportar cookies de BBVA (no usado con login automático)."""
        print("⚠️  Este método ya no es necesario con login automático por credenciales")
