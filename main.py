{\rtf1\ansi\ansicpg1252\cocoartf2822
\cocoatextscaling0\cocoaplatform0{\fonttbl\f0\fswiss\fcharset0 Helvetica;}
{\colortbl;\red255\green255\blue255;}
{\*\expandedcolortbl;;}
\paperw11900\paperh16840\margl1440\margr1440\vieww19680\viewh11580\viewkind0
\pard\tx720\tx1440\tx2160\tx2880\tx3600\tx4320\tx5040\tx5760\tx6480\tx7200\tx7920\tx8640\pardirnatural\partightenfactor0

\f0\fs24 \cf0 import streamlit as st\
import pandas as pd\
import plotly.express as px\
\
# Configuraci\'f3n visual\
st.set_page_config(page_title="ON Investor Pro", layout="wide")\
st.title("\uc0\u55357 \u56960  ON Investor Pro: Gesti\'f3n de Renta Fija")\
\
# --- BASE MAESTRA (Tu valor agregado) ---\
base_maestra = \{\
    "MGCOD": \{"tasa": 0.0787, "sector": "Energ\'eda", "estado": "Vigente"\},\
    "YMCJD": \{"tasa": 0.0900, "sector": "Petr\'f3leo", "estado": "Vigente"\},\
    "MR35D": \{"tasa": 0.0950, "sector": "Alimentos", "estado": "Vigente"\},\
    "GEMSA": \{"tasa": 0.0000, "sector": "Energ\'eda", "estado": "Default"\}\
\}\
\
# --- ESTADO DE LA APP (Simulaci\'f3n de Base de Datos) ---\
if 'cartera' not in st.session_state:\
    st.session_state.cartera = pd.DataFrame(columns=["Ticker", "Cantidad", "Sector", "Cobro_Estimado"])\
\
# --- INTERFAZ DE USUARIO ---\
st.sidebar.header("Men\'fa de Usuario")\
with st.sidebar.expander("\uc0\u10133  Cargar Nuevo Activo"):\
    ticker = st.selectbox("Ticker del Mercado", list(base_maestra.keys()))\
    nominales = st.number_input("Nominales", min_value=0, step=100)\
    if st.button("Guardar en Cartera"):\
        on_info = base_maestra[ticker]\
        nuevo_item = \{\
            "Ticker": ticker, \
            "Cantidad": nominales,\
            "Sector": on_info['sector'],\
            "Cobro_Estimado": (nominales * on_info['tasa']) / 2 if on_info['estado'] == "Vigente" else 0\
        \}\
        st.session_state.cartera = pd.concat([st.session_state.cartera, pd.DataFrame([nuevo_item])], ignore_index=True)\
\
# --- DASHBOARD ---\
col1, col2 = st.columns(2)\
\
with col1:\
    st.subheader("Distribuci\'f3n por Sector")\
    if not st.session_state.cartera.empty:\
        fig_pie = px.pie(st.session_state.cartera, values='Cantidad', names='Sector', hole=0.4)\
        st.plotly_chart(fig_pie)\
\
with col2:\
    st.subheader("Flujo de Fondos Proyectado")\
    if not st.session_state.cartera.empty:\
        fig_bar = px.bar(st.session_state.cartera, x='Ticker', y='Cobro_Estimado', color='Sector')\
        st.plotly_chart(fig_bar)\
\
st.subheader("Tu Detalle de Activos")\
st.table(st.session_state.cartera)}