
import streamlit as st
import pandas as pd
import plotly.express as px
import os
import json

# Estilo XP Inc.
COR_VERDE_XP = "#00582C"
COR_AMARELA_XP = "#FECB00"

st.set_page_config(page_title="XPertESG", layout="wide")

# Carregar dados
df = pd.read_csv("base_clientes_xpertesg.csv")
top_baixa = pd.read_csv("top_baixa.csv")
top_media = pd.read_csv("top_media.csv")
top_alta = pd.read_csv("top_alta.csv")

# Faixas
df["faixa_propensao"] = pd.cut(df["propensao_esg"],
    bins=[0, 0.4, 0.75, 1.0],
    labels=["Baixa", "Média", "Alta"],
    include_lowest=True
)

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
                           color_discrete_sequence=["#00582C", "#FECB00"])
            st.plotly_chart(graf1, use_container_width=True)

            graf2 = px.histogram(df, x="idade", nbins=10, title="Distribuição Etária da Base",
                                 color_discrete_sequence=["#00582C"])
            st.plotly_chart(graf2, use_container_width=True)

    elif aba == "📌 Recomendações":
        st.subheader("📌 Recomendações de Abordagem por Faixa de Propensão ESG")

        st.markdown("### Faixas de Propensão ESG")
        st.markdown("- **Baixa (0.00 – 0.40)**: Informar e educar o cliente sobre ESG.")
        st.markdown("- **Média (0.41 – 0.75)**: Educar e recomendar produtos ESG introdutórios.")
        st.markdown("- **Alta (0.76 – 1.00)**: Foco em conversão com alocação direta em produtos ESG.")

        st.markdown("---")
        st.markdown("### 🎯 Top 5 Clientes de Cada Faixa (Prioridades)")

        st.markdown("#### 🟥 Baixa Propensão – Monitorar e Introduzir ESG")
        st.dataframe(top_baixa, use_container_width=True)

        st.markdown("#### 🟧 Média Propensão – Potenciais Conversões")
        st.dataframe(top_media, use_container_width=True)

        st.markdown("#### 🟩 Alta Propensão – Foco em Alocação")
        st.dataframe(top_alta, use_container_width=True)

    elif aba == "📦 Produtos ESG":
        st.subheader("📦 Produtos ESG Simulados")
        produtos = [
            {"nome": "XP Impacto Sustentável", "tipo": "Fundo Agressivo", "taxa": "1.2%", "liquidez": "D+30", "comissao": "0.7%"},
            {"nome": "XP Clima", "tipo": "Fundo Agressivo", "taxa": "1.0%", "liquidez": "D+60", "comissao": "0.8%"},
            {"nome": "XP Índice Sustentável", "tipo": "Fundo Moderado", "taxa": "0.8%", "liquidez": "D+15", "comissao": "0.6%"},
            {"nome": "XP Essencial ESG", "tipo": "Fundo Conservador", "taxa": "0.5%", "liquidez": "D+5", "comissao": "0.4%"}
        ]
        for p in produtos:
            with st.expander(p["nome"]):
                st.markdown(f"- Tipo: **{p['tipo']}**")
                st.markdown(f"- Taxa: **{p['taxa']}**")
                st.markdown(f"- Liquidez: **{p['liquidez']}**")
                st.markdown(f"- Comissão: **{p['comissao']}**")
