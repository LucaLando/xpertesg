
import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import os
import json

# CONFIGURAÇÃO DE PÁGINA E CSS
st.set_page_config(page_title="XPertESG", layout="wide")

# Inserir logo da XP Inc.
st.sidebar.image("https://seeklogo.com/images/X/xp-inc-logo-083C1A92A7-seeklogo.com.png", width=180)

# CSS customizado XP Inc.
st.markdown(
    '''
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Open Sans', sans-serif;
        background-color: #000000;
        color: #ffffff;
    }

    section[data-testid="stSidebar"] {
        background-color: #000000;
        padding: 1rem;
        border-right: 2px solid #FECB00;
    }

    h1, h2, h3 {
        color: #FECB00;
        font-weight: 700;
    }

    .streamlit-expanderHeader {
        font-weight: bold;
        color: #FECB00;
    }

    button[kind="primary"] {
        background-color: #FECB00 !important;
        color: black !important;
        border-radius: 8px;
        font-weight: bold;
    }

    .stTextInput, .stSelectbox, .stNumberInput, .stTextArea {
        background-color: #111;
        color: white;
        border: 1px solid #FECB00;
    }

    .stDataFrame {
        background-color: #000;
        color: white;
    }

    footer {
        visibility: hidden;
    }
    </style>
    ''',
    unsafe_allow_html=True
)

# SIMULAÇÃO DA BASE DE CLIENTES
df = pd.read_csv("base_clientes_xpertesg.csv")
df["faixa_propensao"] = pd.cut(df["propensao_esg"], bins=[0, 0.4, 0.75, 1.0], labels=["Baixa", "Média", "Alta"])

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

# LOGIN
st.sidebar.markdown("## 👤 Login do Assessor")
usuario_input = st.sidebar.text_input("Digite seu nome de usuário (ex: luca.lando):")
if st.sidebar.button("Entrar") and usuario_input:
    st.session_state.usuario = usuario_input
    st.session_state.mensagens = carregar_historico(usuario_input)
    st.success(f"Bem-vindo, {usuario_input}!")

# SELEÇÃO DE ABA
if st.session_state.usuario:
    st.title(f"📊 XPertESG – Assessor: {st.session_state.usuario}")
    aba = st.sidebar.radio("📂 Escolha uma seção:", [
        "👥 Clientes",
        "🗣️ Chat com o Fábio",
        "📦 Produtos ESG",
        "📈 Dashboards",
        "📌 Recomendações",
        "💡 Alocação Inteligente"
    ])

    if aba == "👥 Clientes":
        st.subheader("📋 Base de Clientes da XP (Simulada)")
        st.dataframe(df, use_container_width=True)

    elif aba == "🗣️ Chat com o Fábio":
        st.subheader("🧠 Fábio – Especialista Virtual ESG")
        with st.expander("🔐 Configurar Chave da API OpenAI"):
            st.session_state.api_key = st.text_input("Cole aqui sua API Key:", type="password")
        prompt_usuario = st.text_area("Digite sua pergunta para o Fábio:")
        if st.button("Enviar") and prompt_usuario and st.session_state.api_key:
            st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})
            openai.api_key = st.session_state.api_key
            try:
                resposta = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Você é o Fábio, um especialista em investimentos com foco em ESG. Responda como um assistente da XP Inc., sempre com foco consultivo, educacional e técnico para assessores de investimento."}
                    ] + st.session_state.mensagens,
                    temperature=0.7,
                    max_tokens=700
                )
                resposta_fabio = resposta.choices[0].message.content
                st.session_state.mensagens.append({"role": "assistant", "content": resposta_fabio})
                salvar_historico(st.session_state.usuario, st.session_state.mensagens)
            except Exception as e:
                resposta_fabio = f"Erro na chamada à API: {str(e)}"
                st.session_state.mensagens.append({"role": "assistant", "content": resposta_fabio})
        for msg in st.session_state.mensagens:
            st.markdown(f"**{'Você' if msg['role']=='user' else 'Fábio'}:** {msg['content']}")

# OBS: Aqui viriam as outras abas (Produtos ESG, Dashboards, Recomendações, Alocação Inteligente),
# que devem ser adicionadas a seguir com base nos blocos que você já possui, preservando todas as seções.

