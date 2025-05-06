
import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import os
import json

# Config
st.set_page_config(page_title="XPertESG", layout="wide")
COR_XP = "#FECB00"

# Dados
df = pd.read_csv("base_clientes_xpertesg.csv")
df["faixa_propensao"] = pd.cut(df["propensao_esg"], bins=[0, 0.4, 0.75, 1.0], labels=["Baixa", "Média", "Alta"])

top_baixa = df[df["faixa_propensao"] == "Baixa"].nlargest(5, "propensao_esg")
top_media = df[df["faixa_propensao"] == "Média"].nlargest(5, "propensao_esg")
top_alta = df[df["faixa_propensao"] == "Alta"].nlargest(5, "propensao_esg")

# Sessões
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

# Interface
if st.session_state.usuario:
    st.title(f"XPertESG – Assessor: {st.session_state.usuario}")
    aba = st.sidebar.radio("Navegar para:", ["👥 Clientes", "🗣️ Chat com o Fábio", "📦 Produtos ESG", "📈 Dashboards", "📌 Recomendações", "💡 Alocação Inteligente"])

    if aba == "👥 Clientes":
        subaba = st.radio("Selecione a visualização:", ["📋 Perfis dos Clientes"])
        if subaba == "📋 Perfis dos Clientes":
            st.subheader("📋 Base de Clientes da XP (Simulada)")
            st.dataframe(df, use_container_width=True)

    elif aba == "🗣️ Chat com o Fábio":
        st.subheader("Fábio – Especialista Virtual ESG")

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

    elif aba == "📈 Dashboards":
        st.subheader("📊 Análise ESG da Base de Clientes")
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(df.groupby("perfil_risco")["propensao_esg"].mean().reset_index(),
                          x="perfil_risco", y="propensao_esg", color="perfil_risco",
                          color_discrete_sequence=[COR_XP])
            fig1.update_traces(marker_line_color='black', marker_line_width=1.5)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.histogram(df, x="idade", nbins=10, title="Distribuição Etária da Base",
                                color_discrete_sequence=[COR_XP])
            fig2.update_traces(marker_line_color='black', marker_line_width=1.5)
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            fig3 = px.pie(df, names="faixa_propensao", title="Distribuição por Faixa ESG",
                          color_discrete_sequence=[COR_XP])
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            fig4 = px.bar(df.nlargest(5, "propensao_esg"),
                          x="nome", y="propensao_esg", title="Top 5 Clientes com Maior Propensão ESG",
                          color_discrete_sequence=[COR_XP])
            fig4.update_traces(marker_line_color='black', marker_line_width=1.5)
            st.plotly_chart(fig4, use_container_width=True)

    
        st.subheader("📌 Recomendações de Abordagem por Faixa de Propensão ESG")

        st.markdown("### Faixas de Propensão ESG")
        st.markdown("- **Baixa (0.00 – 0.40)**: Informar e educar o cliente sobre ESG.")
        st.markdown("- **Média (0.41 – 0.75)**: Educar e recomendar produtos ESG introdutórios.")
        st.markdown("- **Alta (0.76 – 1.00)**: Foco em conversão com alocação direta em produtos ESG.")
        st.markdown("---")

        st.markdown("### 🎯 Top 5 Clientes por Faixa com Ação Recomendada")
        for cliente in top_baixa["nome"]:
            st.info(f"{st.session_state.usuario}, fale com **{cliente}** e explique os benefícios de produtos ESG.")
        for cliente in top_media["nome"]:
            st.warning(f"{st.session_state.usuario}, recomende um produto introdutório para **{cliente}**.")
        for cliente in top_alta["nome"]:
            st.success(f"{st.session_state.usuario}, aloque capital de **{cliente}** em um fundo ESG imediatamente.")

    st.subheader("💡 Proposta de Alocação Inteligente com Produtos ESG")

    cliente_escolhido = st.selectbox("Selecione um cliente para análise:", df["nome"])
    cliente_info = df[df["nome"] == cliente_escolhido].iloc[0]
    perfil = cliente_info["perfil_risco"]

    st.markdown(f"**Perfil de Investidor XP**: {perfil}")

    carteira_atual = {
        "Renda Fixa": 40 if perfil == "Conservador" else 25,
        "Fundos Multimercado": 30 if perfil == "Moderado" else 20,
        "Ações": 20 if perfil == "Agressivo" else 10,
        "Caixa": 10
    }

    st.markdown("### 📦 Composição Atual da Carteira (Simulada)")
    st.write(carteira_atual)

    substituiveis = {
        "Renda Fixa": "XP Essencial ESG",
        "Fundos Multimercado": "XP Índice Sustentável",
        "Ações": "XP Impacto Sustentável"
    }

    st.markdown("### ♻️ Sugestões ESG com base nos ativos atuais:")
    nova_carteira = {}
    for ativo, perc in carteira_atual.items():
        if ativo in substituiveis:
            produto_esg = substituiveis[ativo]
            st.info(f"🔁 Substituir parte de **{ativo}** por **{produto_esg}** mantendo liquidez semelhante.")
            nova_carteira[produto_esg] = perc
        else:
            nova_carteira[ativo] = perc

    st.markdown("### 📈 Proposta de Nova Carteira com Alocação ESG:")
    st.write(nova_carteira)
    st.success("✅ Proposta pronta para apresentação ao cliente.")
