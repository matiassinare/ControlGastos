import pandas as pd
import random
from datetime import datetime, timedelta
import uuid

class MockDataGenerator:
    """
    Generates realistic mock data for the Expense Tracker.
    """
    
    def __init__(self):
        self.categories = [
            'Supermercado', 'Restaurante', 'Servicios', 'Transporte',
            'Entretenimiento', 'Shopping', 'Suscripciones', 'Viajes'
        ]
        
        self.merchants = {
            'Supermercado': ['Coto', 'Carrefour', 'Jumbo', 'Dia%', 'Chino'],
            'Restaurante': ['McDonalds', 'Burger King', 'La Farola', 'Kentucky', 'Sushi Club', 'Starbucks'],
            'Servicios': ['Edesur', 'Metrogas', 'AySA', 'Personal', 'Movistar', 'Cablevision'],
            'Transporte': ['Uber', 'Cabify', 'Carga SUBE', 'Shell', 'YPF'],
            'Entretenimiento': ['Cinema', 'Teatro Colon', 'Hoyts'],
            'Shopping': ['Zara', 'Adidas', 'Nike', 'Uniqlo', 'MercadoLibre'],
            'Suscripciones': ['Netflix', 'Spotify', 'Youtube Premium', 'iCloud', 'OpenAI'],
            'Viajes': ['Aerolineas Argentinas', 'Booking.com', 'Despegar']
        }
        
        self.banks = ['BBVA', 'Galicia']
        self.currencies = ['ARS', 'USD']

    def generate_transactions(self, count: int = 50, months_back: int = 3) -> pd.DataFrame:
        """
        Generate a DataFrame of mock transactions.
        
        Args:
            count: Number of transactions to generate.
            months_back: How many months back to go.
            
        Returns:
            pd.DataFrame with columns: id, date, description, amount, currency, bank, category
        """
        data = []
        end_date = datetime.now()
        start_date = end_date - timedelta(days=30*months_back)
        
        for _ in range(count):
            # Random date
            days_delta = (end_date - start_date).days
            random_days = random.randint(0, days_delta)
            date = start_date + timedelta(days=random_days)
            
            # Random category and merchant
            category = random.choice(self.categories)
            merchant = random.choice(self.merchants[category])
            
            # Random amount (weighted by category)
            if category == 'Supermercado':
                amount = random.uniform(5000, 50000)
            elif category == 'Restaurante':
                amount = random.uniform(3000, 20000)
            elif category == 'Servicios':
                amount = random.uniform(2000, 15000)
            elif category == 'Suscripciones':
                amount = random.uniform(1000, 8000)
            elif category == 'Transporte':
                amount = random.uniform(500, 40000) # SUBE is low, but Gas/Uber can be higher
            else:
                amount = random.uniform(2000, 100000)
                
            # Random currency (mostly ARS)
            currency = 'ARS'
            if category in ['Suscripciones', 'Viajes'] and random.random() > 0.7:
                currency = 'USD'
                amount = amount / 1000 # Rough conversion for USD amounts
                
            # Random bank
            bank = random.choice(self.banks)

            # Asignar statement_period basado en el mes de la transacción
            statement_period = f"{date.year}-{date.month:02d}"

            data.append({
                'id': str(uuid.uuid4()),
                'date': date.date(),
                'description': f"COMPRA EN {merchant.upper()}",
                'amount': round(amount, 2),
                'currency': currency,
                'bank': bank,
                'category': category,
                'installments': '1/1',
                'statement_period': statement_period
            })

        # Ensure columns exist even if empty
        cols = ['id', 'date', 'description', 'amount', 'currency', 'bank', 'category', 'installments', 'statement_period']
        df = pd.DataFrame(data, columns=cols)
        
        if not df.empty:
            df = df.sort_values('date', ascending=False).reset_index(drop=True)
            
        return df

    def get_summary_kpis(self, df: pd.DataFrame):
        """Calculate basic KPIs from dataframe."""
        total_ars = df[df['currency'] == 'ARS']['amount'].sum()
        total_usd = df[df['currency'] == 'USD']['amount'].sum()
        count = len(df)
        return total_ars, total_usd, count
