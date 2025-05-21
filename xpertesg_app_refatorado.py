
import os
import json
from datetime import datetime
import streamlit as st
import pandas as pd
import numpy as np
import openai

# Constants and Configurations
NAMES_MALE = [
    "João", "Pedro", "Miguel", "Lucas", "Gustavo",
    "Rafael", "Mateus", "Bruno", "Carlos", "Felipe"
]
NAMES_FEMALE = [
    "Ana", "Beatriz", "Camila", "Daniela", "Fernanda",
    "Gabriela", "Helena", "Isabela", "Juliana", "Karen"
]
PRODUCTS_ESG = [
    {"nome": "Fundo XP Essencial ESG", "tipo": "Renda Fixa", "risco": "Baixo", "taxa": "0,9% a.a."},
    {"nome": "ETF XP Sustentável", "tipo": "ETF", "risco": "Médio", "taxa": "0,3% a.a."},
    {"nome": "Fundo XP Verde Ações", "tipo": "Ações", "risco": "Alto", "taxa": "1,2% a.a."}
]

SYSTEM_PROMPT = {
    "role": "system",
    "content": (
        "Você é Fábio, o assistente virtual ESG da XP Inc. "
        "Forneça recomendações e suporte técnico a assessores de investimentos "
        "com uma linguagem empresarial e alinhada ao tom de voz da XP Inc."
    )
}

MAX_HISTORY = 20
HISTORY_FILE = "history.json"

# Setup
st.set_page_config(page_title="XPertESG", layout="wide")
openai.api_key = os.getenv("OPENAI_API_KEY")

@st.cache_data
def load_data(path):
    """Carrega e retorna o DataFrame."""
    try:
        df = pd.read_csv(path)
        return df
    except Exception as e:
        st.error(f"Erro ao carregar base de dados: {e}")
        return pd.DataFrame()

def assign_names(df):
    """Atribui nomes aleatórios conforme o gênero."""
    mask_m = df["Genero"] == "Masculino"
    mask_f = df["Genero"] == "Feminino"
    df.loc[mask_m, "Nome"] = np.random.choice(NAMES_MALE, mask_m.sum())
    df.loc[mask_f, "Nome"] = np.random.choice(NAMES_FEMALE, mask_f.sum())
    return df

def load_history():
    """Carrega histórico de conversas."""
    try:
        with open(HISTORY_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        return []

def save_history(history):
    """Salva histórico de conversas."""
    try:
        with open(HISTORY_FILE, "w", encoding="utf-8") as f:
            json.dump(history, f, ensure_ascii=False, indent=2)
    except Exception as e:
        st.warning(f"Não foi possível salvar histórico: {e}")

def show_dashboard(df):
    """Exibe dashboards básicos."""
    with st.spinner("Gerando dashboards..."):
        st.header("📈 Dashboards ESG")
        # Exemplo de métrica
        if "ESG_Label" in df.columns:
            percent_esg = df["ESG_Label"].mean() * 100
            st.metric("Clientes ESG (%)", f"{percent_esg:.1f}%")
        # Exemplo de gráfico simples
        if "Propensao_ESG" in df.columns:
            st.line_chart(df["Propensao_ESG"])

def chat_section():
    """Seção de chat com Fábio."""
    st.header("💬 Chat com Fábio")
    if "history" not in st.session_state:
        st.session_state.history = load_history()

    user_input = st.text_input("Pergunte algo ao Fábio:")
    if st.button("Enviar") and user_input:
        # Atualiza histórico
        st.session_state.history.append({"role": "user", "content": user_input})
        # Prepara mensagens
        messages = [SYSTEM_PROMPT] + st.session_state.history
        # Limita histórico para tokens
        if len(messages) > MAX_HISTORY:
            messages = messages[-MAX_HISTORY:]
        # Chamada à API
        try:
            response = openai.ChatCompletion.create(
                model="gpt-4o-mini",
                messages=messages
            )
            reply = response.choices[0].message
            st.session_state.history.append({"role": reply["role"], "content": reply["content"]})
            save_history(st.session_state.history)
            st.write(reply["content"])
        except Exception as e:
            st.error(f"Erro na API do OpenAI: {e}")

def main():
    st.sidebar.title("XPertESG")
    st.sidebar.info("Configure sua chave da OpenAI como variável de ambiente OPENAI_API_KEY")
    # Carregar dados
    with st.spinner("Carregando base de dados..."):
        df = load_data("base5_clientes_esg10000.csv")
    df = assign_names(df)
    # Navegação
    page = st.sidebar.selectbox("Navegação", ["📋 Dados", "📈 Dashboards", "💬 Chat"])
    if page == "📋 Dados":
        st.header("Dados brutos")
        st.write(df)
    elif page == "📈 Dashboards":
        show_dashboard(df)
    else:
        chat_section()

if __name__ == "__main__":
    main()
