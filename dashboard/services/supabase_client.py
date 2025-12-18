"""
Cliente Supabase Simplificado
Conexión directa para uso personal.
"""

import streamlit as st
from supabase import create_client, Client

@st.cache_resource
def get_supabase_client() -> Client:
    """
    Obtener cliente de Supabase (singleton).
    Retorna None si no hay credenciales (para modo mock).
    """
    try:
        supabase_url = st.secrets["supabase"]["url"]
        supabase_key = st.secrets["supabase"]["key"]
        return create_client(supabase_url, supabase_key)
    except Exception:
        return None
