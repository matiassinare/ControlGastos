import pandas as pd
import streamlit as st
from datetime import date, datetime
from services.supabase_client import get_supabase_client
from services.mock_data import MockDataGenerator

class DataService:
    """
    Service to handle data retrieval for the dashboard.
    Abstracts the source (Supabase or Mock).
    """

    def __init__(self, use_mock: bool = False):
        self.use_mock = use_mock
        self.mock_generator = MockDataGenerator()
        self.supabase = get_supabase_client()

    def _serialize_for_supabase(self, data: dict) -> dict:
        """Convert Python objects to JSON-serializable formats for Supabase."""
        serialized = data.copy()
        for key, value in serialized.items():
            if isinstance(value, (date, datetime)):
                serialized[key] = value.isoformat()
        return serialized

    def get_transactions(self, limit: int = 100) -> pd.DataFrame:
        """
        Fetch transactions.
        """
        # Fallback: Force mock if usage is requested OR supabase is missing
        should_use_mock = self.use_mock or (self.supabase is None)
        
        if not self.use_mock and self.supabase is None:
            st.warning("⚠️ No se detectaron credenciales de Supabase. Usando modo Mock.", icon="⚠️")

        if should_use_mock:
            # Cache mock data in session state to persist between re-runs
            if 'mock_transactions' not in st.session_state:
                # Initialize with empty data (user wants only imported data)
                st.session_state.mock_transactions = self.mock_generator.generate_transactions(count=0)
            return st.session_state.mock_transactions
        
        # Else: Fetch from Supabase
        try:
            response = self.supabase.table('transactions').select('*').order('date', desc=True).limit(limit).execute()
            data = response.data
            if not data:
                return pd.DataFrame()
            
            df = pd.DataFrame(data)
            # Ensure correct types
            df['date'] = pd.to_datetime(df['date']).dt.date
            df['amount'] = df['amount'].astype(float)
            return df
        except Exception as e:
            st.error(f"Error fetching data from Supabase: {e}")
            return pd.DataFrame()

    def add_manual_transaction(self, data: dict):
        """
        Add a manual transaction.
        Returns True if successful, False if duplicate/error.
        Modifies data dict in-place to add 'id' field.
        """
        import uuid

        if self.use_mock:
            # Add to local session state mock
            if 'mock_transactions' not in st.session_state:
                # Initialize if not present (e.g. user went straight to import)
                st.session_state.mock_transactions = self.mock_generator.generate_transactions(count=0)

            # Check for duplicates (same date, description, amount)
            current_df = st.session_state.mock_transactions
            if not current_df.empty:
                # Ensure date comparison works (both should be date objects or comparable)
                # data['date'] comes from PDF parser as date object.
                duplicate_mask = (
                    (current_df['date'] == data['date']) &
                    (current_df['description'] == data['description']) &
                    (abs(current_df['amount'] - data['amount']) < 0.01) # Float tolerance
                )
                if not current_df[duplicate_mask].empty:
                    return False # Skip duplicate

            # Add ID
            data['id'] = str(uuid.uuid4())
            # Add to dataframe
            new_row = pd.DataFrame([data])
            st.session_state.mock_transactions = pd.concat([new_row, st.session_state.mock_transactions], ignore_index=True)
            st.session_state.mock_transactions = st.session_state.mock_transactions.sort_values('date', ascending=False)
            return True
        else:
            try:
                # Generate ID before inserting (Supabase auto-generates, but we need it for cuotas)
                if 'id' not in data or data['id'] is None:
                    data['id'] = str(uuid.uuid4())

                # Serialize dates before sending to Supabase
                serialized_data = self._serialize_for_supabase(data)
                response = self.supabase.table('transactions').insert(serialized_data).execute()

                # Update data with the actual ID from Supabase if it returns one
                if response.data and len(response.data) > 0:
                    if 'id' in response.data[0]:
                        data['id'] = response.data[0]['id']

                return True
                return True
            except Exception as e:
                st.error(f"Error inserting to Supabase: {e}")
                return False

    def update_transaction(self, transaction_id: str, updates: dict) -> bool:
        """
        Update a transaction in Supabase (or mock).
        """
        if self.use_mock:
            # Update in local session state mock
            if 'mock_transactions' in st.session_state:
                df = st.session_state.mock_transactions
                if not df.empty and 'id' in df.columns:
                    # Find and update
                    mask = df['id'] == transaction_id
                    if mask.any():
                        for key, value in updates.items():
                             df.loc[mask, key] = value
                        st.session_state.mock_transactions = df
                        return True
            return False
        else:
            try:
                # Update in Supabase
                self.supabase.table('transactions').update(updates).eq('id', transaction_id).execute()
                return True
            except Exception as e:
                st.error(f"Error updating Supabase: {e}")
                return False

    def delete_transaction(self, transaction_id: str) -> bool:
        """
        Delete a transaction from Supabase (or mock).
        """
        if self.use_mock:
            if 'mock_transactions' in st.session_state:
                df = st.session_state.mock_transactions
                if not df.empty and 'id' in df.columns:
                    st.session_state.mock_transactions = df[df['id'] != transaction_id]
                    return True
            return False
        else:
            try:
                self.supabase.table('transactions').delete().eq('id', transaction_id).execute()
                return True
            except Exception as e:
                st.error(f"Error deleting from Supabase: {e}")
                return False

def get_data_service():
    """Factory to get data service based on config."""
    # Use Supabase by default (no mock mode)
    use_mock = st.session_state.get('use_mock_data', False)
    return DataService(use_mock=use_mock)
