import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

st.set_page_config(page_title="ON Investor Pro", layout="wide")

# Conexión con manejo de errores para que no se caiga la app
try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception:
    st.error("Error en la configuración de Secrets. Revisá el formato TOML.")
    st.stop()

st.title("🚀 ON Investor Pro")

# Formulario de carga
with st.sidebar.form("nueva_on"):
    st.header("Cargar Activo")
    user = st.text_input("Usuario (Email)")
    ticker = st.selectbox("Ticker", ["MGCOD", "YMCJD", "MR35D", "IRCPD", "GEMSA"])
    cantidad = st.number_input("Cantidad", min_value=1)
    if st.form_submit_button("Guardar Permanentemente"):
        if user:
            nueva_fila = {"email": user, "sheet_url": f"{ticker}:{cantidad}"}
            conn.table("usuarios_config").insert(nueva_fila).execute()
            st.success("¡Guardado en la base de datos!")
            st.rerun()
        else:
            st.warning("Por favor ingresá un usuario.")

# Mostrar tabla de datos
try:
    res = conn.table("usuarios_config").select("*").execute()
    df = pd.DataFrame(res.data)
    if not df.empty:
        st.subheader("Tu Cartera Guardada")
        st.dataframe(df)
    else:
        st.info("La base de datos está vacía.")
except Exception as e:
    st.info("Conexión establecida. Cargá un dato para inicializar.")
