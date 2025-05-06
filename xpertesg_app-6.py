
import streamlit as st
import pandas as pd
import requests
import plotly.express as px

st.set_page_config(page_title="XPertESG", layout="wide")

# Carregar dados
df = pd.read_csv("base_clientes_xpertesg.csv")

# Estado de sessão
if "api_key" not in st.session_state:
    st.session_state.api_key = ""
if "mensagens" not in st.session_state:
    st.session_state.mensagens = []

# Título
st.title("XPertESG – Plataforma para Assessores")

# Menu lateral
aba = st.sidebar.radio("Navegar para:", ["📊 Dashboard", "🗣️ Chat com o Fábio"])

# ========== DASHBOARD ==========
if aba == "📊 Dashboard":
    st.subheader("📊 Análise ESG da Base de Clientes")

    st.dataframe(df, use_container_width=True)

    st.markdown("### Propensão ESG média por perfil de risco")
    graf1 = px.bar(
        df.groupby("perfil_risco")["propensao_esg"].mean().reset_index(),
        x="perfil_risco",
        y="propensao_esg",
        color="perfil_risco",
        title="Média de Propensão ESG por Perfil de Risco"
    )
    st.plotly_chart(graf1, use_container_width=True)

    st.markdown("### Distribuição de Idade dos Clientes")
    graf2 = px.histogram(
        df, x="idade", nbins=10,
        title="Distribuição Etária da Base",
        color_discrete_sequence=["#00582C"]
    )
    st.plotly_chart(graf2, use_container_width=True)

# ========== CHAT ==========
elif aba == "🗣️ Chat com o Fábio":
    col1, col2 = st.columns([1, 10])
    with col1:
        st.image("https://upload.wikimedia.org/wikipedia/commons/thumb/7/70/User_icon_BLACK-01.png/480px-User_icon_BLACK-01.png", width=60, caption="Fábio")
    with col2:
        st.subheader("Fábio – Assistente Virtual do Assessor")

    with st.expander("🔐 Configurar Chave da API OpenAI"):
        st.session_state.api_key = st.text_input("Cole aqui sua API Key:", type="password")

    cliente_id = st.number_input("ID do cliente que deseja consultar:", min_value=1, max_value=len(df), step=1)
    prompt_usuario = st.text_area("Digite sua pergunta para o Fábio:", key="input_msg")

    if st.button("Enviar") and prompt_usuario and st.session_state.api_key:
        st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})
        cliente = df[df["id"] == cliente_id].iloc[0]
        prop = cliente["propensao_esg"]

        if prop >= 0.6:
            conduta = "alocar recursos e recomendar produtos ESG avançados como o XP Impacto Sustentável ou XP Clima."
        elif prop >= 0.3:
            conduta = "educar o cliente sobre ESG e recomendar produtos introdutórios como o XP Índice Sustentável."
        else:
            conduta = "informar o cliente sobre ESG e monitorar possíveis mudanças de interesse."

        resposta_fabio = f"O cliente **{cliente['nome']}** possui propensão ESG de **{prop:.2f}**. Minha recomendação é: **{conduta}**"
        st.session_state.mensagens.append({"role": "assistant", "content": resposta_fabio})

    for msg in st.session_state.mensagens:
        if msg["role"] == "user":
            st.markdown(f"**Você:** {msg['content']}")
        else:
            st.markdown(f"**Fábio:** {msg['content']}")
