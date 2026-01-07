import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="ON Investor Pro", layout="wide")
st.title("🚀 ON Investor Pro")

# Intentamos conectar usando los secretos
try:
    # Esta es la forma estándar de Streamlit para conectar
    conn = st.connection("supabase", type=SupabaseConnection)
    
    # Probamos una consulta simple para ver si hay conexión real
    res = conn.table("usuarios_config").select("email").limit(1).execute()
    st.success("¡Conexión establecida con éxito!")
    
    # Formulario de prueba
    with st.form("test_form"):
        email = st.text_input("Tu nombre/email para probar")
        if st.form_submit_button("Verificar Base de Datos"):
            st.write(f"Hola {email}, la base de datos te reconoce.")

except Exception as e:
    st.error("Todavía hay un problema con las credenciales en 'Secrets'.")
    st.info("Asegurate de que en Secrets diga [connections.supabase] con la 'url' y la 'key' correctamente.")
    st.write("Detalle técnico del error:", e)
