
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# Cores padrão XP Inc.
COR_VERDE_XP = "#00582C"
COR_AMARELA_XP = "#FECB00"

st.set_page_config(page_title="XPertESG", layout="wide")

# Carregar dados base
df = pd.read_csv("base_clientes_xpertesg.csv")

# Criar faixas de propensão ESG
df["faixa_propensao"] = pd.cut(
    df["propensao_esg"],
    bins=[0, 0.4, 0.75, 1.0],
    labels=["Baixa", "Média", "Alta"],
    include_lowest=True
)

# Calcular Top 5 por faixa (os mais próximos do limite superior)
top_baixa = df[df["faixa_propensao"] == "Baixa"].nlargest(5, "propensao_esg")
top_media = df[df["faixa_propensao"] == "Média"].nlargest(5, "propensao_esg")
top_alta = df[df["faixa_propensao"] == "Alta"].nlargest(5, "propensao_esg")

# Sessão
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

def carregar_historico(usuario):
    arq = f"historico_{usuario}.json"
    return json.load(open(arq, encoding="utf-8")) if os.path.exists(arq) else []

def salvar_historico(usuario, mensagens):
    with open(f"historico_{usuario}.json", "w", encoding="utf-8") as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=2)

# Login
st.sidebar.markdown("## 👤 Login do Assessor")
usuario_input = st.sidebar.text_input("Digite seu nome de usuário (ex: luca.lando):")
if st.sidebar.button("Entrar") and usuario_input:
    st.session_state.usuario = usuario_input
    st.session_state.mensagens = carregar_historico(usuario_input)
    st.success(f"Bem-vindo, {usuario_input}!")

if st.session_state.usuario:
    st.title(f"XPertESG – Assessor: {st.session_state.usuario}")
    aba = st.sidebar.radio("Navegar para:", ["👥 Clientes", "🗣️ Chat com o Fábio", "📦 Produtos ESG", "📌 Recomendações"])

    if aba == "👥 Clientes":
        subaba = st.radio("Selecione a visualização:", ["📋 Perfis dos Clientes", "📈 Dashboards"])
        if subaba == "📋 Perfis dos Clientes":
            st.subheader("📋 Base de Clientes da XP (Simulada)")
            st.dataframe(df, use_container_width=True)
        elif subaba == "📈 Dashboards":
            st.subheader("📊 Análise ESG da Base de Clientes")

            graf1 = px.bar(df.groupby("perfil_risco")["propensao_esg"].mean().reset_index(),
                        x="perfil_risco", y="propensao_esg", color="perfil_risco",
                        color_discrete_sequence=["#FECB00"])
            graf1.update_traces(marker_line_color='black', marker_line_width=1.5)
            st.plotly_chart(graf1, use_container_width=True)

            graf2 = px.histogram(df, x="idade", nbins=10, title="Distribuição Etária da Base",
                                color_discrete_sequence=["#FECB00"])
            graf2.update_traces(marker_line_color='black', marker_line_width=1.5)
            st.plotly_chart(graf2, use_container_width=True)

            st.markdown("### 🏆 Top 5 Clientes Mais Propensos ESG")
            top_5 = df.nlargest(5, "propensao_esg")
            graf_top = px.bar(top_5,
                            x="nome", y="propensao_esg",
                            title="Top 5 Clientes com Maior Propensão ESG",
                            color_discrete_sequence=["#FECB00"])
            graf_top.update_traces(marker_line_color='black', marker_line_width=1.5)
            col1, col2 = st.columns(2)
            with col1:
                st.plotly_chart(graf_top, use_container_width=True)
