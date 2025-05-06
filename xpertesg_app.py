
import streamlit as st
import pandas as pd

st.set_page_config(page_title="XPertESG", layout="wide")

st.title("XPertESG - Dashboard de Clientes")

df = pd.read_csv("base_clientes_xpertesg.csv")

st.dataframe(df)

st.markdown("### Análise rápida:")
st.bar_chart(df.groupby("perfil_risco")["propensao_esg"].mean())
