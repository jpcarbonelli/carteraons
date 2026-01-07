import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

st.title("🚀 ON Investor Pro")

# --- CONEXIÓN DIRECTA (A prueba de errores) ---
# Buscamos las llaves directamente en la raíz de los secrets
try:
    # Intentamos obtener los valores directamente
    s_url = st.secrets["connections"]["supabase"]["url"]
    s_key = st.secrets["connections"]["supabase"]["key"]
    
    # Creamos la conexión pasando los parámetros manualmente
    conn = st.connection(
        "supabase", 
        type=SupabaseConnection,
        url=s_url,
        key=s_key
    )
    
    # Prueba de lectura
    res = conn.table("usuarios_config").select("*").limit(1).execute()
    st.success("¡CONECTADO CON ÉXITO! La base de datos responde.")
    st.dataframe(pd.DataFrame(res.data))

except Exception as e:
    st.error("Error de configuración de credenciales")
    st.write("Asegurate de que tus Secrets sigan exactamente el formato TOML de abajo.")
    st.code("""
[connections.supabase]
url = "tu_url_aqui"
key = "tu_key_aqui"
    """, language="toml")
    st.write("Detalle del error:", e)
