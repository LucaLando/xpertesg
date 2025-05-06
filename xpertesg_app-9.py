
import streamlit as st
import pandas as pd
import requests
import plotly.express as px
import os
import json

st.set_page_config(page_title="XPertESG", layout="wide")

# Base de clientes e produtos ESG (simulada)
df = pd.read_csv("base_clientes_xpertesg.csv")
produtos = [
    {"nome": "XP Impacto Sustentável", "tipo": "Fundo Agressivo", "taxa": "1.2%", "liquidez": "D+30", "comissao": "0.7%"},
    {"nome": "XP Clima", "tipo": "Fundo Agressivo", "taxa": "1.0%", "liquidez": "D+60", "comissao": "0.8%"},
    {"nome": "XP Índice Sustentável", "tipo": "Fundo Moderado", "taxa": "0.8%", "liquidez": "D+15", "comissao": "0.6%"},
    {"nome": "XP Essencial ESG", "tipo": "Fundo Conservador", "taxa": "0.5%", "liquidez": "D+5", "comissao": "0.4%"}
]

# Sessão
if "usuario" not in st.session_state:
    st.session_state.usuario = ""
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

def carregar_historico(usuario):
    arquivo = f"historico_{usuario}.json"
    if os.path.exists(arquivo):
        with open(arquivo, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def salvar_historico(usuario, mensagens):
    arquivo = f"historico_{usuario}.json"
    with open(arquivo, "w", encoding="utf-8") as f:
        json.dump(mensagens, f, ensure_ascii=False, indent=2)

# LOGIN
st.sidebar.markdown("## 👤 Login do Assessor")
usuario_input = st.sidebar.text_input("Digite seu nome de usuário (ex: luca.lando):")
if st.sidebar.button("Entrar") and usuario_input:
    st.session_state.usuario = usuario_input
    st.session_state.mensagens = carregar_historico(usuario_input)
    st.success(f"Bem-vindo, {usuario_input}!")

if st.session_state.usuario:
    st.title(f"XPertESG – Assessor: {st.session_state.usuario}")
    aba = st.sidebar.radio("Navegar para:", ["📊 Dashboard", "🗣️ Chat com o Fábio", "📦 Produtos ESG"])

    if aba == "📊 Dashboard":
        st.subheader("📊 Análise ESG da Base de Clientes")
        st.dataframe(df, use_container_width=True)

        st.markdown("### Propensão ESG média por perfil de risco")
        graf1 = px.bar(
            df.groupby("perfil_risco")["propensao_esg"].mean().reset_index(),
            x="perfil_risco", y="propensao_esg", color="perfil_risco",
            title="Média de Propensão ESG por Perfil de Risco"
        )
        st.plotly_chart(graf1, use_container_width=True)

        st.markdown("### Distribuição Etária dos Clientes")
        graf2 = px.histogram(df, x="idade", nbins=10, title="Distribuição Etária da Base",
                             color_discrete_sequence=["#00582C"])
        st.plotly_chart(graf2, use_container_width=True)

    elif aba == "🗣️ Chat com o Fábio":
        col1, col2 = st.columns([1, 10])
        with col1:
            st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/User_icon_BLACK-01.png/480px-User_icon_BLACK-01.png", width=60, caption="Fábio")
        with col2:
            st.subheader("Fábio – Assistente Virtual do Assessor")

        with st.expander("🔐 Configurar Chave da API OpenAI"):
            st.session_state.api_key = st.text_input("Cole aqui sua API Key:", type="password")

        cliente_id = st.number_input("ID do cliente que deseja consultar:", min_value=1, max_value=len(df), step=1)
        prompt_usuario = st.text_area("Digite sua pergunta para o Fábio:")

        if st.button("Enviar") and prompt_usuario and st.session_state.api_key:
            st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})
            cliente = df[df["id"] == cliente_id].iloc[0]
            prop = cliente["propensao_esg"]

            if prop >= 0.6:
                produto = produtos[0]
                conduta = f"alocar recursos no fundo **{produto['nome']}** (Taxa: {produto['taxa']}, Liquidez: {produto['liquidez']}, Comissão: {produto['comissao']})."
                explicacao = "Este cliente possui forte inclinação para investimentos sustentáveis, conforme histórico e perfil de risco."
            elif prop >= 0.3:
                produto = produtos[2]
                conduta = f"educar sobre ESG e apresentar o produto **{produto['nome']}** (Taxa: {produto['taxa']}, Liquidez: {produto['liquidez']}, Comissão: {produto['comissao']})."
                explicacao = "O cliente demonstra interesse médio por ESG, sendo recomendada uma abordagem mais educativa."
            else:
                produto = produtos[3]
                conduta = f"informar sobre conceitos de ESG e acompanhar evolução. Produto sugerido: **{produto['nome']}** (Taxa: {produto['taxa']}, Liquidez: {produto['liquidez']}, Comissão: {produto['comissao']})."
                explicacao = "Baixa propensão ESG; priorize sensibilização e acompanhamento gradual."

            resposta_fabio = (
                f"O cliente **{cliente['nome']}** possui propensão ESG de **{prop:.2f}**.\n\n"
                f"📊 **Análise Técnica:** {explicacao}\n\n"
                f"📌 **Recomendação:** {conduta}"
            )
            st.session_state.mensagens.append({"role": "assistant", "content": resposta_fabio})
            salvar_historico(st.session_state.usuario, st.session_state.mensagens)

        for msg in st.session_state.mensagens:
            if msg["role"] == "user":
                st.markdown(f"**Você:** {msg['content']}")
            else:
                st.markdown(f"**Fábio:** {msg['content']}")

    elif aba == "📦 Produtos ESG":
        st.subheader("📦 Catálogo de Produtos ESG da XP (Simulados)")
        for produto in produtos:
            with st.expander(produto["nome"]):
                st.markdown(f"- Tipo: **{produto['tipo']}**")
                st.markdown(f"- Taxa de administração: **{produto['taxa']}**")
                st.markdown(f"- Liquidez: **{produto['liquidez']}**")
                st.markdown(f"- Comissão para assessor: **{produto['comissao']}**")
