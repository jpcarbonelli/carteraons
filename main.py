import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

# Conexión optimizada
conn = st.connection("supabase", type=SupabaseConnection)

st.title("🚀 Mi Cartera Permanente")

# Función para leer la tabla usuarios_config
def cargar_datos():
    try:
        # Traemos las columnas que tenés: email y sheet_url
        res = conn.table("usuarios_config").select("email, sheet_url").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.error(f"Error de conexión: {e}")
        return pd.DataFrame(columns=["email", "sheet_url"])

# --- FORMULARIO ---
with st.sidebar.form("form_registro"):
    user = st.text_input("Usuario (Email)")
    on_ticker = st.selectbox("ON", ["MGCOD", "YMCJD", "MR35D", "IRCPD"])
    cantidad = st.number_input("Cantidad", min_value=1)
    
    if st.form_submit_button("Guardar Datos"):
        # Guardamos en tu tabla real
        nueva_fila = {"email": user, "sheet_url": f"{on_ticker}:{cantidad}"}
        conn.table("usuarios_config").insert(nueva_fila).execute()
        st.success("¡Guardado!")
        st.rerun()

# --- VISTA ---
df = cargar_datos()
if not df.empty:
    st.write("Datos en la Nube:")
    st.dataframe(df)
