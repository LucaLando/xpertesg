
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
import json

COR_VERDE_XP = "#00582C"
COR_AMARELA_XP = "#FECB00"

st.set_page_config(page_title="XPertESG", layout="wide")

df = pd.read_csv("base_clientes_xpertesg.csv")
produtos = [
    {"nome": "XP Impacto Sustentável", "tipo": "Fundo Agressivo", "taxa": "1.2%", "liquidez": "D+30", "comissao": "0.7%"},
    {"nome": "XP Clima", "tipo": "Fundo Agressivo", "taxa": "1.0%", "liquidez": "D+60", "comissao": "0.8%"},
    {"nome": "XP Índice Sustentável", "tipo": "Fundo Moderado", "taxa": "0.8%", "liquidez": "D+15", "comissao": "0.6%"},
    {"nome": "XP Essencial ESG", "tipo": "Fundo Conservador", "taxa": "0.5%", "liquidez": "D+5", "comissao": "0.4%"}
]

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

# Estilo customizado
st.markdown(f"""<style>
.st-emotion-cache-6qob1r {{
    background-color: {COR_VERDE_XP};
    color: white;
}}
.stButton > button {{
    background-color: {COR_AMARELA_XP};
    color: black;
    font-weight: bold;
}}
</style>""", unsafe_allow_html=True)

# Logo superior da XPertESG
st.image("xpertesg_logo.png", width=180)

st.sidebar.markdown("## 👤 Login do Assessor")
usuario_input = st.sidebar.text_input("Digite seu nome de usuário (ex: luca.lando):")
if st.sidebar.button("Entrar") and usuario_input:
    st.session_state.usuario = usuario_input
    st.session_state.mensagens = carregar_historico(usuario_input)
    st.success(f"Bem-vindo, {usuario_input}!")

if st.session_state.usuario:
    st.title(f"XPertESG – Assessor: {st.session_state.usuario}")
    aba = st.sidebar.radio("Navegar para:", ["👥 Clientes", "🗣️ Chat com o Fábio", "📦 Produtos ESG"])

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

    elif aba == "🗣️ Chat com o Fábio":
        st.subheader("Fábio – Assistente Virtual do Assessor")
        st.image("fabio_avatar.png", width=100)

        with st.expander("🔐 Configurar Chave da API OpenAI"):
            st.session_state.api_key = st.text_input("Cole aqui sua API Key:", type="password")

        cliente_id = st.number_input("ID do cliente:", min_value=1, max_value=len(df), step=1)
        prompt_usuario = st.text_area("Mensagem para o Fábio:")

        if st.button("Enviar") and prompt_usuario and st.session_state.api_key:
            st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})
            cliente = df[df["id"] == cliente_id].iloc[0]
            prop = cliente["propensao_esg"]
            if prop >= 0.6:
                produto, explicacao = produtos[0], "forte inclinação para ESG."
            elif prop >= 0.3:
                produto, explicacao = produtos[2], "interesse médio por ESG."
            else:
                produto, explicacao = produtos[3], "baixa propensão ESG."

            conduta = f"Produto sugerido: **{produto['nome']}** (Taxa: {produto['taxa']}, Liquidez: {produto['liquidez']}, Comissão: {produto['comissao']})."
            resposta = f"O cliente **{cliente['nome']}** possui propensão ESG de **{prop:.2f}**.\n\n📊 **Análise:** {explicacao}\n\n📌 {conduta}"
            st.session_state.mensagens.append({"role": "assistant", "content": resposta})
            salvar_historico(st.session_state.usuario, st.session_state.mensagens)

        for msg in st.session_state.mensagens:
            st.markdown(f"**{'Você' if msg['role']=='user' else 'Fábio'}:** {msg['content']}")

    elif aba == "📦 Produtos ESG":
        st.subheader("📦 Produtos ESG Simulados")
        for p in produtos:
            with st.expander(p["nome"]):
                st.markdown(f"- Tipo: **{p['tipo']}**")
                st.markdown(f"- Taxa: **{p['taxa']}**")
                st.markdown(f"- Liquidez: **{p['liquidez']}**")
                st.markdown(f"- Comissão: **{p['comissao']}**")
