import streamlit as st
import pandas as pd
from st_supabase_connection import SupabaseConnection

st.title("🚀 ON Investor Pro")

try:
    conn = st.connection("supabase", type=SupabaseConnection)
    res = conn.table("usuarios_config").select("*").execute()
    st.success("¡Conexión exitosa con la base de datos!")
    st.dataframe(pd.DataFrame(res.data))
except Exception as e:
    st.error(f"Error: {e}")
