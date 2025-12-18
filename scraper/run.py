#!/usr/bin/env python3
"""
Expense Tracker - Scraper Entry Point

Script principal para scrapear tarjetas de crédito y guardar transacciones en Supabase.

Uso:
    python run.py scrape                    # Scrapear todas las tarjetas
    python run.py scrape --bank bbva        # Solo BBVA
    python run.py scrape --bank galicia     # Solo Galicia
    python run.py export-cookies --bank bbva  # Exportar cookies BBVA
    python run.py --help                    # Ver ayuda
"""

import argparse
import sys
import os
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno
load_dotenv()

# Verificar que las credenciales de Supabase estén configuradas
if not os.getenv('SUPABASE_URL') or not os.getenv('SUPABASE_KEY'):
    print("❌ ERROR: Falta configurar SUPABASE_URL y SUPABASE_KEY en el archivo .env")
    print("Por favor, copiar .env.example como .env y completar las credenciales.")
    sys.exit(1)


def export_cookies(bank: str):
    """
    Exportar cookies de un banco específico.

    Args:
        bank: 'bbva' o 'galicia'
    """
    print(f"\n🍪 Exportando cookies de {bank.upper()}...\n")

    from credit_card_scraper import CreditCardScraper

    scraper = CreditCardScraper()

    try:
        if bank == 'bbva':
            scraper.export_bbva_cookies()
        elif bank == 'galicia':
            scraper.export_galicia_cookies()
        else:
            print(f"❌ Banco '{bank}' no soportado. Usar: bbva, galicia")
            sys.exit(1)

        print(f"\n✅ Cookies de {bank.upper()} exportadas exitosamente")

    except Exception as e:
        print(f"\n❌ Error exportando cookies: {e}")
        sys.exit(1)


def scrape(bank: str = None, verbose: bool = False):
    """
    Scrapear transacciones de tarjetas.

    Args:
        bank: Banco específico ('bbva', 'galicia') o None para todos
        verbose: Mostrar logs detallados
    """
    print("\n💳 Iniciando scraper de tarjetas...\n")

    from credit_card_scraper import CreditCardScraper

    scraper = CreditCardScraper(verbose=verbose)

    try:
        results = scraper.scrape_all(bank_filter=bank)

        # Mostrar resumen
        print("\n" + "=" * 60)
        print("📊 RESUMEN DE SCRAPING")
        print("=" * 60)

        total_transactions = 0
        for bank_name, data in results.items():
            print(f"\n{bank_name}:")
            print(f"  ✓ Transacciones encontradas: {data['found']}")
            print(f"  ✓ Nuevas insertadas: {data['inserted']}")
            print(f"  ✓ Duplicadas (omitidas): {data['duplicates']}")
            total_transactions += data['inserted']

        print("\n" + "=" * 60)
        print(f"✅ TOTAL: {total_transactions} transacciones nuevas insertadas")
        print("=" * 60 + "\n")

        if total_transactions == 0:
            print("ℹ️  No hay transacciones nuevas. Posibles razones:")
            print("   - Ya fueron scrapeadas previamente")
            print("   - No hay movimientos en el último mes")
            print("   - Cookies expiradas (ejecutar: python run.py export-cookies)\n")

    except Exception as e:
        print(f"\n❌ Error durante el scraping: {e}")
        if verbose:
            import traceback
            traceback.print_exc()
        sys.exit(1)


def main():
    """Entry point principal."""
    parser = argparse.ArgumentParser(
        description="Expense Tracker - Scraper de tarjetas de crédito",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Ejemplos de uso:
  python run.py scrape                      # Scrapear todas las tarjetas
  python run.py scrape --bank bbva          # Solo BBVA
  python run.py scrape --bank galicia       # Solo Galicia
  python run.py scrape --verbose            # Con logs detallados
  python run.py export-cookies --bank bbva  # Exportar cookies BBVA

Bancos soportados:
  - bbva: BBVA Visa
  - galicia: Galicia Visa y Amex
        """
    )

    subparsers = parser.add_subparsers(dest='command', help='Comando a ejecutar')

    # Comando: scrape
    scrape_parser = subparsers.add_parser('scrape', help='Scrapear transacciones')
    scrape_parser.add_argument(
        '--bank',
        choices=['bbva', 'galicia'],
        help='Banco específico (omitir para scrapear todos)'
    )
    scrape_parser.add_argument(
        '--verbose',
        action='store_true',
        help='Mostrar logs detallados y capturas de pantalla'
    )

    # Comando: export-cookies
    export_parser = subparsers.add_parser('export-cookies', help='Exportar cookies de un banco')
    export_parser.add_argument(
        '--bank',
        choices=['bbva', 'galicia'],
        required=True,
        help='Banco del cual exportar cookies'
    )

    args = parser.parse_args()

    # Ejecutar comando
    if args.command == 'scrape':
        scrape(bank=args.bank, verbose=args.verbose)

    elif args.command == 'export-cookies':
        export_cookies(bank=args.bank)

    else:
        parser.print_help()


if __name__ == '__main__':
    main()
