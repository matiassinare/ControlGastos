"""
Convertir cookies de diferentes formatos a JSON para Playwright
"""

import json
import sys
from pathlib import Path

def netscape_to_playwright(netscape_file: str, output_file: str):
    """
    Convertir formato Netscape (cookies.txt) a formato Playwright JSON.

    Args:
        netscape_file: Archivo cookies.txt
        output_file: Archivo JSON de salida
    """
    cookies = []

    with open(netscape_file, 'r') as f:
        for line in f:
            # Saltar comentarios y líneas vacías
            if line.startswith('#') or not line.strip():
                continue

            parts = line.strip().split('\t')

            if len(parts) < 7:
                continue

            domain, _, path, secure, expires, name, value = parts

            cookie = {
                'name': name,
                'value': value,
                'domain': domain,
                'path': path,
                'expires': int(expires) if expires != '0' else -1,
                'httpOnly': False,
                'secure': secure.upper() == 'TRUE',
                'sameSite': 'Lax'
            }

            cookies.append(cookie)

    # Guardar en formato JSON
    with open(output_file, 'w') as f:
        json.dump(cookies, f, indent=2)

    print(f"✅ Convertidas {len(cookies)} cookies")
    print(f"📁 Guardadas en: {output_file}")


def chrome_json_to_playwright(chrome_file: str, output_file: str):
    """
    Convertir cookies de Chrome DevTools (JSON) a formato Playwright.

    Args:
        chrome_file: Archivo JSON de Chrome
        output_file: Archivo JSON de salida
    """
    with open(chrome_file, 'r') as f:
        chrome_cookies = json.load(f)

    playwright_cookies = []

    for cookie in chrome_cookies:
        playwright_cookie = {
            'name': cookie.get('name', ''),
            'value': cookie.get('value', ''),
            'domain': cookie.get('domain', ''),
            'path': cookie.get('path', '/'),
            'expires': cookie.get('expirationDate', -1),
            'httpOnly': cookie.get('httpOnly', False),
            'secure': cookie.get('secure', False),
            'sameSite': cookie.get('sameSite', 'Lax')
        }

        playwright_cookies.append(playwright_cookie)

    with open(output_file, 'w') as f:
        json.dump(playwright_cookies, f, indent=2)

    print(f"✅ Convertidas {len(playwright_cookies)} cookies")
    print(f"📁 Guardadas en: {output_file}")


if __name__ == '__main__':
    if len(sys.argv) < 3:
        print("Uso:")
        print("  python convert_cookies.py cookies.txt bbva.json")
        print("  python convert_cookies.py chrome_cookies.json bbva.json")
        sys.exit(1)

    input_file = sys.argv[1]
    output_file = sys.argv[2]

    # Detectar formato
    if input_file.endswith('.txt'):
        print("📄 Detectado formato Netscape (cookies.txt)")
        netscape_to_playwright(input_file, output_file)
    else:
        print("📄 Detectado formato JSON")
        chrome_json_to_playwright(input_file, output_file)

    print(f"\n💡 Ahora movelo a: .cookies/{Path(output_file).name}")
