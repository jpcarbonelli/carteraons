import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

# Conexión ultra-segura a Supabase
conn = st.connection("supabase", type=SupabaseConnection, ttl=0)

st.title("🚀 Mi Cartera Permanente")

# Función para traer los datos guardados
def cargar_datos():
    try:
        # Traemos email (como usuario) y sheet_url (donde guardaremos el ticker:cantidad)
        res = conn.table("usuarios_config").select("email, sheet_url").execute()
        return pd.DataFrame(res.data)
    except:
        return pd.DataFrame(columns=["email", "sheet_url"])

# --- FORMULARIO DE CARGA ---
with st.sidebar.form("formulario_on"):
    st.header("Cargar Activo")
    user_email = st.text_input("Tu Email o Nombre")
    ticker = st.selectbox("Ticker", ["MGCOD", "YMCJD", "MR35D", "IRCPD", "GEMSA"])
    cantidad = st.number_input("Cantidad", min_value=1)
    
    if st.form_submit_button("Guardar en la Nube"):
        # Guardamos el formato "TICKER:CANTIDAD" en la columna sheet_url
        data_to_save = {"email": user_email, "sheet_url": f"{ticker}:{cantidad}"}
        conn.table("usuarios_config").insert(data_to_save).execute()
        st.success("¡Datos guardados!")
        st.rerun()

# --- MOSTRAR CARTERA ---
st.subheader("Registros en Base de Datos")
df = cargar_datos()

if not df.empty:
    st.table(df)
else:
    st.info("La base de datos está vacía. Cargá algo desde el costado.")
