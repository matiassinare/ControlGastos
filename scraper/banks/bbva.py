import asyncio
import json
import os
import time
from datetime import datetime
from typing import Dict, List, Optional
from playwright.sync_api import sync_playwright, Page, BrowserContext

# Import utils
try:
    from scraper.utils import parse_amount, parse_date
except ImportError:
    # Handle running from different context
    import sys
    sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from utils import parse_amount, parse_date

class BBVAScraper:
    """
    Scraper for BBVA Argentina Online Banking.
    Uses Playwright to navigate and extract data.
    """
    
    def __init__(self, verbose: bool = False, headless: bool = False):
        self.verbose = verbose
        # We might want non-headless for debugging or CAPTCHAs initially
        self.headless = headless 
        self.base_url = "https://bancalinea.bbva.com.ar/login"
        self.cookies_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'cookies', 'bbva.json')
        
        # Ensure cookies dir exists
        os.makedirs(os.path.dirname(self.cookies_path), exist_ok=True)

    def log(self, msg: str):
        if self.verbose:
            print(f"[BBVA] {msg}")

    def login(self):
        """
        Attempts to login using saved cookies.
        If not logged in, pauses for manual login.
        """
        self.playwright = sync_playwright().start()
        # Launch browser - consider using 'chrome' if chromium has issues with some banks
        self.browser = self.playwright.chromium.launch(headless=self.headless, slow_mo=500)
        
        # Create context
        self.context = self.browser.new_context(
            viewport={'width': 1280, 'height': 800},
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        
        # Load cookies if exist
        if os.path.exists(self.cookies_path):
            self.log(f"Loading cookies from {self.cookies_path}")
            with open(self.cookies_path, 'r') as f:
                cookies = json.load(f)
                self.context.add_cookies(cookies)
        
        self.page = self.context.new_page()
        
        self.log(f"Navigating to {self.base_url}")
        self.page.goto(self.base_url)
        
        # Check if logged in
        # This selector depends on the bank's dashboard. 
        # Usually looking for "Cerrar sesión" or "Mis Productos"
        try:
            # Wait a bit for redirects
            self.page.wait_for_load_state('networkidle')
            
            # Simple check: are we on the login page still?
            if "login" in self.page.url:
                self.log("Not logged in automatically.")
                self._manual_login()
            else:
                self.log("Apparently logged in.")
                
        except Exception as e:
            self.log(f"Error checking login status: {e}")
            self._manual_login()

    def _manual_login(self):
        """
        Pause execution to allow user to log in manually.
        """
        print("\n" + "!"*60)
        print("⚠️  LOGIN REQUERIDO")
        print("El navegador se abrirá. Por favor iniciá sesión manualmente en BBVA.")
        print("Una vez que veas tu posición consolidada (cuentas/tarjetas), presiona ENTER en esta terminal.")
        print("!"*60 + "\n")
        
        # If we were headless, we need to restart as headed needed
        if self.headless:
            self.close()
            self.headless = False
            self.login() # Recursive call with headless=False
            return

        input("Presiona ENTER cuando hayas iniciado sesión...")
        
        # Save cookies after manual login
        self.save_cookies()

    def save_cookies(self):
        """Save current cookies to file."""
        cookies = self.context.cookies()
        with open(self.cookies_path, 'w') as f:
            json.dump(cookies, f)
        self.log(f"Cookies saved to {self.cookies_path}")

    def export_cookies(self):
        """Only login and save cookies, then exit."""
        # Force headed mode for export
        self.headless = False 
        try:
            self.login()
            # If login returned, we are good (it asks for manual login if needed)
            print("✅ Cookies exportadas correctamente.")
        finally:
            self.close()

    def get_data(self) -> List[Dict]:
        """
        Scrape credit card data.
        Assumes we are logged in.
        """
        transactions = []
        
        try:
            self.log("Navigating to Credit Cards section...")
            # Attempt to find common BBVA entry points
            # Usually there is a cards menu or a specific card container
            
            # Debug: Screenshot of initial dashboard
            if self.verbose:
                self.save_debug_snapshot("dashboard_initial")

            # Try to find something that looks like a card
            # Identifiers often used: "Tarjetas", "Visa", "Mastercard", "Ultimos movimientos"
            
            # Simple heuristic: Look for "Tarjetas" link/button
            try:
                # Wait for potential dynamic content
                self.page.wait_for_selector("text=Tarjetas", timeout=5000)
                self.page.get_by_text("Tarjetas", exact=False).first.click()
            except Exception:
                self.log("Could not click 'Tarjetas'. Trying direct URL or alternative selectors.")
                # Fallback: maybe we are already there or need another click
            
            self.page.wait_for_load_state('networkidle')
            if self.verbose:
                self.save_debug_snapshot("cards_view")

            # Try to grab transactions from a table
            # Common selectors for tables: 'table', '.movements', 
            # We will try to find a table and dump its text if we can't parse it yet
            
            rows = self.page.locator("table tr").all()
            if not rows:
                self.log("No table rows found. Trying to find list items...")
                rows = self.page.locator(".transaction-item").all() # Generic class guess

            self.log(f"Found {len(rows)} potential rows/items.")
            
            # Placeholder: extract text from first few rows to see what we have
            for i, row in enumerate(rows[:5]):
                self.log(f"Row {i}: {row.inner_text()}")

            # TODO: Real parsing based on inspection of "Row X" output
            
        except Exception as e:
            self.log(f"Error scraping data: {e}")
            self.save_debug_snapshot("error_state")
            if self.verbose:
                import traceback
                traceback.print_exc()
            
        finally:
            self.close()
            
        return transactions

    def save_debug_snapshot(self, name: str):
        """Save HTML and Screenshot for debugging."""
        try:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            debug_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'debug')
            os.makedirs(debug_dir, exist_ok=True)
            
            # Screenshot
            shot_path = os.path.join(debug_dir, f"{name}_{timestamp}.png")
            self.page.screenshot(path=shot_path)
            self.log(f"Saved screenshot: {shot_path}")
            
            # HTML
            html_path = os.path.join(debug_dir, f"{name}_{timestamp}.html")
            with open(html_path, 'w', encoding='utf-8') as f:
                f.write(self.page.content())
            self.log(f"Saved HTML: {html_path}")
            
        except Exception as e:
            self.log(f"Failed to save debug snapshot: {e}")


    def close(self):
        if hasattr(self, 'browser'):
            self.browser.close()
        if hasattr(self, 'playwright'):
            self.playwright.stop()
