
import streamlit as st
import pandas as pd
import requests

st.set_page_config(page_title="XPertESG", layout="wide")

# Simulação de chave API (provisório)
if "api_key" not in st.session_state:
    st.session_state.api_key = ""

# Título fixo
st.title("XPertESG – Plataforma para Assessores")

# Menu lateral para navegação
aba = st.sidebar.radio("Navegar para:", ["📊 Dashboard", "🗣️ Chat com o Fábio"])

# ========== ABA 1: DASHBOARD ==========
if aba == "📊 Dashboard":
    st.subheader("📊 Análise da Base de Clientes XP (Simulada)")

    df = pd.read_csv("base_clientes_xpertesg.csv")
    st.dataframe(df, use_container_width=True)

    st.markdown("### Propensão ESG média por perfil de risco")
    st.bar_chart(df.groupby("perfil_risco")["propensao_esg"].mean())

    st.markdown("### Distribuição por faixa etária")
    st.hist(df["idade"], bins=10, use_container_width=True)

# ========== ABA 2: CHAT COM O FÁBIO ==========
elif aba == "🗣️ Chat com o Fábio":
    st.subheader("🧑‍💼 Fábio – Assistente Virtual do Assessor")

    if "mensagens" not in st.session_state:
        st.session_state.mensagens = []

    with st.expander("🔐 Configurar Chave da API OpenAI"):
        st.session_state.api_key = st.text_input("Cole aqui sua API Key:", type="password")

    prompt_usuario = st.text_area("Digite sua pergunta para o Fábio:", key="input_msg")
    if st.button("Enviar") and prompt_usuario and st.session_state.api_key:

        # Armazenar pergunta
        st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})

        # Montar payload da OpenAI
        payload = {
            "model": "gpt-4",
            "messages": [
                {"role": "system", "content": "Você é o ExpertESG, uma IA que auxilia um assistente virtual chamado Fábio. Responda de forma técnica e clara, voltado para o assessor de investimentos da XP Inc."}
            ] + st.session_state.mensagens
        }

        headers = {
            "Authorization": f"Bearer {st.session_state.api_key}",
            "Content-Type": "application/json"
        }

        # Enviar para OpenAI
        try:
            resposta = requests.post("https://api.openai.com/v1/chat/completions",
                                     json=payload, headers=headers)
            resposta_json = resposta.json()
            mensagem_fabio = resposta_json["choices"][0]["message"]["content"]
            st.session_state.mensagens.append({"role": "assistant", "content": mensagem_fabio})
        except:
            st.error("Erro ao se comunicar com a API da OpenAI. Verifique a chave e tente novamente.")

    # Mostrar histórico
    for msg in st.session_state.mensagens:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content']}")
        else:
            st.markdown(f"**Fábio:** {msg['content']}")
