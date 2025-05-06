
import streamlit as st
import pandas as pd
import requests
import matplotlib.pyplot as plt

st.set_page_config(page_title="XPertESG", layout="wide")

# Chave da API
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

st.title("XPertESG – Plataforma para Assessores")

aba = st.sidebar.radio("Navegar para:", ["📊 Dashboard", "🗣️ Chat com o Fábio"])

# ABA 1 – DASHBOARD
if aba == "📊 Dashboard":
    st.subheader("📊 Análise da Base de Clientes XP (Simulada)")

    df = pd.read_csv("base_clientes_xpertesg.csv")
    st.dataframe(df, use_container_width=True)

    st.markdown("### Propensão ESG média por perfil de risco")
    st.bar_chart(df.groupby("perfil_risco")["propensao_esg"].mean())

    st.markdown("### Distribuição por faixa etária")
    fig, ax = plt.subplots()
    ax.hist(df["idade"], bins=10, color="#00582C", edgecolor="white")
    ax.set_xlabel("Idade")
    ax.set_ylabel("Quantidade de clientes")
    ax.set_title("Distribuição de Idade dos Clientes")
    st.pyplot(fig)

# ABA 2 – CHAT COM O FÁBIO
elif aba == "🗣️ Chat com o Fábio":
    st.subheader("🧑‍💼 Fábio – Assistente Virtual do Assessor")

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    with st.expander("🔐 Configurar Chave da API OpenAI"):
        st.session_state.api_key = st.text_input("Cole aqui sua API Key:", type="password")

    prompt_usuario = st.text_area("Digite sua pergunta para o Fábio:", key="input_msg")
    if st.button("Enviar") and prompt_usuario and st.session_state.api_key:
        st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})

        payload = {
            "model": "gpt-3.5-turbo",  # substituído para garantir compatibilidade
            "messages": [
                {"role": "system", "content": "Você é o ExpertESG, uma IA que auxilia um assistente virtual chamado Fábio. Responda de forma técnica e clara, voltado para o assessor de investimentos da XP Inc."}
            ] + st.session_state.mensagens
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.api_key}",
            "Content-Type": "application/json"
        }

        try:
            resposta = requests.post("https://api.openai.com/v1/chat/completions",
                                     json=payload, headers=headers)
            resposta.raise_for_status()
            resposta_json = resposta.json()
            mensagem_fabio = resposta_json["choices"][0]["message"]["content"]
            st.session_state.mensagens.append({"role": "assistant", "content": mensagem_fabio})
        except Exception as e:
            st.error(f"Erro ao se comunicar com a API da OpenAI: {e}")

    for msg in st.session_state.mensagens:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content']}")
        else:
            st.markdown(f"**Fábio:** {msg['content']}")
