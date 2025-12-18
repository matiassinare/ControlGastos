#!/usr/bin/env python3
"""
Script de verificación de setup del proyecto.
Ejecutar antes de comenzar el desarrollo para verificar que todo esté correcto.
"""

import os
from pathlib import Path

# Colores para terminal
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
RESET = '\033[0m'

def check_file(path):
    """Verificar si un archivo existe."""
    if os.path.exists(path):
        print(f"{GREEN}✓{RESET} {path}")
        return True
    else:
        print(f"{RED}✗{RESET} {path} - FALTA")
        return False

def check_directory(path):
    """Verificar si un directorio existe."""
    if os.path.isdir(path):
        print(f"{GREEN}✓{RESET} {path}/")
        return True
    else:
        print(f"{RED}✗{RESET} {path}/ - FALTA")
        return False

def main():
    print("\n" + "="*60)
    print("🔍 VERIFICACIÓN DE ESTRUCTURA DEL PROYECTO")
    print("="*60 + "\n")

    checks_passed = 0
    total_checks = 0

    # Directorios
    print("📁 Directorios:")
    directories = [
        'database',
        'docs',
        'scraper',
        'scraper/banks',
        'dashboard',
        'dashboard/pages',
        'dashboard/components',
        'dashboard/services',
        'dashboard/.streamlit',
        '.github',
        '.github/workflows',
        '.github/ISSUE_TEMPLATE'
    ]

    for directory in directories:
        if check_directory(directory):
            checks_passed += 1
        total_checks += 1

    # Archivos principales
    print("\n📄 Archivos de configuración:")
    config_files = [
        'README.md',
        'LICENSE',
        'CONTRIBUTING.md',
        '.gitignore'
    ]

    for file in config_files:
        if check_file(file):
            checks_passed += 1
        total_checks += 1

    # Database
    print("\n🗄️ Base de datos:")
    db_files = [
        'database/schema.sql',
        'database/policies.sql',
        'database/seed.sql'
    ]

    for file in db_files:
        if check_file(file):
            checks_passed += 1
        total_checks += 1

    # Docs
    print("\n📚 Documentación:")
    doc_files = [
        'docs/ARCHITECTURE.md',
        'docs/SETUP_SUPABASE.md',
        'docs/SETUP_STREAMLIT.md',
        'docs/SETUP_SCRAPER.md'
    ]

    for file in doc_files:
        if check_file(file):
            checks_passed += 1
        total_checks += 1

    # Scraper
    print("\n🤖 Scraper:")
    scraper_files = [
        'scraper/__init__.py',
        'scraper/run.py',
        'scraper/requirements.txt',
        'scraper/.env.example',
        'scraper/banks/__init__.py'
    ]

    for file in scraper_files:
        if check_file(file):
            checks_passed += 1
        total_checks += 1

    # Dashboard
    print("\n🎨 Dashboard:")
    dashboard_files = [
        'dashboard/streamlit_app.py',
        'dashboard/requirements.txt',
        'dashboard/secrets.toml.example',
        'dashboard/.streamlit/config.toml',
        'dashboard/components/__init__.py',
        'dashboard/services/__init__.py',
        'dashboard/services/supabase_client.py'
    ]

    for file in dashboard_files:
        if check_file(file):
            checks_passed += 1
        total_checks += 1

    # GitHub
    print("\n🔧 GitHub:")
    github_files = [
        '.github/ISSUE_TEMPLATE/bug_report.md',
        '.github/ISSUE_TEMPLATE/feature_request.md',
        '.github/PULL_REQUEST_TEMPLATE.md'
    ]

    for file in github_files:
        if check_file(file):
            checks_passed += 1
        total_checks += 1

    # Resumen
    print("\n" + "="*60)
    percentage = (checks_passed / total_checks) * 100

    if percentage == 100:
        print(f"{GREEN}✅ ESTRUCTURA COMPLETA{RESET}")
    elif percentage >= 80:
        print(f"{YELLOW}⚠️  ESTRUCTURA CASI COMPLETA ({percentage:.1f}%){RESET}")
    else:
        print(f"{RED}❌ ESTRUCTURA INCOMPLETA ({percentage:.1f}%){RESET}")

    print(f"\nVerificaciones: {checks_passed}/{total_checks} pasadas")
    print("="*60 + "\n")

    # Warnings
    if not os.path.exists('scraper/.env'):
        print(f"{YELLOW}⚠️{RESET}  Recordar: copiar scraper/.env.example como scraper/.env")

    if not os.path.exists('dashboard/.streamlit/secrets.toml'):
        print(f"{YELLOW}⚠️{RESET}  Recordar: copiar dashboard/secrets.toml.example como dashboard/.streamlit/secrets.toml")

    print()

if __name__ == '__main__':
    main()
