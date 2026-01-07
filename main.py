import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

# Configuración de página
st.set_page_config(page_title="ON Investor Pro", layout="wide")

# Conexión con manejo de errores
try:
    conn = st.connection("supabase", type=SupabaseConnection)
except Exception:
    st.error("Error en la configuración de Secrets. Revisá el formato TOML.")
    st.stop()

st.title("🚀 Mi Cartera Permanente")

# Función para leer datos
def cargar_datos():
    try:
        # Consultamos tu tabla real
        res = conn.table("usuarios_config").select("*").execute()
        return pd.DataFrame(res.data)
    except Exception as e:
        st.info("La base de datos está conectada. Cargá tu primer activo para ver la tabla.")
        return pd.DataFrame()

# --- FORMULARIO LATERAL ---
with st.sidebar.form("registro_on"):
    st.header("Nuevo Registro")
    user = st.text_input("Usuario (Email)")
    on_ticker = st.selectbox("Seleccioná ON", ["MGCOD", "YMCJD", "MR35D", "IRCPD", "GEMSA"])
    cantidad = st.number_input("Cantidad", min_value=1, step=1)
    
    if st.form_submit_button("Guardar en Supabase"):
        if user:
            # Insertamos en las columnas que tenés: email y sheet_url
            nueva_on = {"email": user, "sheet_url": f"{on_ticker}:{cantidad}"}
            conn.table("usuarios_config").insert(nueva_on).execute()
            st.success("¡Guardado!")
            st.rerun()
        else:
            st.warning("Por favor, poné un nombre de usuario.")

# --- CUERPO PRINCIPAL ---
df = cargar_datos()
if not df.empty:
    st.subheader("Datos guardados en la Nube")
    # Limpiamos un poco la vista del DF
    st.dataframe(df[["email", "sheet_url"]], use_container_width=True)
