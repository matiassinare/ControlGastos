"""
Script para inspeccionar bancos manualmente con Playwright Inspector
"""

import sys
from playwright.sync_api import sync_playwright

def inspect_bbva():
    """Inspeccionar BBVA."""
    print("\n🔍 INSPECTOR DE BBVA")
    print("="*60)
    print("1. Se abrirá el navegador")
    print("2. Logueate manualmente")
    print("3. Navegá a la sección de tarjetas")
    print("4. En el inspector de Playwright podés:")
    print("   - Hacer click en elementos para ver sus selectores")
    print("   - Copiar selectores CSS/XPath")
    print("   - Probar locators en la consola")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # Habilitar inspector
        page.pause()

        # Ir a BBVA
        page.goto('https://www.bbva.com.ar')

        print("\n💡 Inspecciona el sitio y anota:")
        print("   - Selector de la tabla de transacciones")
        print("   - Selector de cada columna (fecha, descripción, monto)")
        print("   - Cómo se llega a la sección de tarjetas")

        input("\nPresioná ENTER cuando termines...")

        browser.close()

def inspect_galicia():
    """Inspeccionar Galicia."""
    print("\n🔍 INSPECTOR DE GALICIA")
    print("="*60)
    print("1. Se abrirá el navegador")
    print("2. Logueate manualmente")
    print("3. Navegá a la sección de tarjetas")
    print("4. En el inspector de Playwright podés:")
    print("   - Hacer click en elementos para ver sus selectores")
    print("   - Copiar selectores CSS/XPath")
    print("   - Probar locators en la consola")
    print("="*60)

    with sync_playwright() as p:
        browser = p.chromium.launch(headless=False, slow_mo=500)
        context = browser.new_context()
        page = context.new_page()

        # Habilitar inspector
        page.pause()

        # Ir a Galicia
        page.goto('https://onlinebanking.bancogalicia.com.ar/inicio')

        print("\n💡 Inspecciona el sitio y anota:")
        print("   - Selector de la tabla de transacciones")
        print("   - Selector de cada columna (fecha, descripción, monto)")
        print("   - Cómo se llega a la sección de tarjetas")
        print("   - Diferencias entre Visa y Amex")

        input("\nPresioná ENTER cuando termines...")

        browser.close()

if __name__ == '__main__':
    if len(sys.argv) < 2:
        print("Uso: python inspect_bank.py [bbva|galicia]")
        sys.exit(1)

    bank = sys.argv[1].lower()

    if bank == 'bbva':
        inspect_bbva()
    elif bank == 'galicia':
        inspect_galicia()
    else:
        print("Banco no soportado. Usar: bbva o galicia")
