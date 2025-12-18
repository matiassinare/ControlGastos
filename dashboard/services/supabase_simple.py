"""
Cliente Supabase Simplificado
Sin autenticación - conexión directa
"""

import streamlit as st
from supabase import create_client, Client


@st.cache_resource
def get_supabase_client() -> Client:
    """
    Obtener cliente de Supabase (singleton).
    Sin autenticación - usa service role key.

    Returns:
        Client: Cliente de Supabase
    """
    supabase_url = st.secrets["supabase"]["url"]
    supabase_key = st.secrets["supabase"]["key"]

    return create_client(supabase_url, supabase_key)
