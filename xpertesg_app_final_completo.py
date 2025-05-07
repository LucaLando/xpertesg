
import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import os
import json

st.set_page_config(page_title="XPertESG", layout="wide")
COR_XP = "#FECB00"

# Dados simulados
df = pd.read_csv("base_clientes_xpertesg.csv")
df["faixa_propensao"] = pd.cut(df["propensao_esg"], bins=[0, 0.4, 0.75, 1.0], labels=["Baixa", "Mdia", "Alta"])

top_baixa = df[df["faixa_propensao"] == "Baixa"].nlargest(5, "propensao_esg")
top_media = df[df["faixa_propensao"] == "Mdia"].nlargest(5, "propensao_esg")
top_alta = df[df["faixa_propensao"] == "Alta"].nlargest(5, "propensao_esg")

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

st.sidebar.markdown("##  Login do Assessor")
usuario_input = st.sidebar.text_input("Digite seu nome de usurio (ex: luca.lando):")
if st.sidebar.button("Entrar") and usuario_input:
    st.session_state.usuario = usuario_input
    st.session_state.mensagens = carregar_historico(usuario_input)
    st.success(f"Bem-vindo, {usuario_input}!")

if st.session_state.usuario:
    st.title(f"XPertESG  Assessor: {st.session_state.usuario}")
    aba = st.sidebar.radio("Escolha uma seo:", [
        " Clientes",
        " Chat com o Fbio",
        " Produtos ESG",
        " Dashboards",
        " Recomendaes",
        " Alocao Inteligente"
    ])

    if aba == " Clientes":
        st.subheader(" Base de Clientes da XP (Simulada)")
        st.dataframe(df, use_container_width=True)

    elif aba == " Chat com o Fbio":
        st.subheader("Fbio  Especialista Virtual ESG")
        with st.expander(" Configurar Chave da API OpenAI"):
            st.session_state.api_key = st.text_input("Cole aqui sua API Key:", type="password")
        prompt_usuario = st.text_area("Digite sua pergunta para o Fbio:")
        if st.button("Enviar") and prompt_usuario and st.session_state.api_key:
            st.session_state.mensagens.append({"role": "user", "content": prompt_usuario})
            openai.api_key = st.session_state.api_key
            try:
                resposta = openai.ChatCompletion.create(
                    model="gpt-4",
                    messages=[
                        {"role": "system", "content": "Voc  o Fbio, um especialista em investimentos com foco em ESG. Responda como um assistente da XP Inc., sempre com foco consultivo, educacional e tcnico para assessores de investimento."}
                    ] + st.session_state.mensagens,
                    temperature=0.7,
                    max_tokens=700
                )
                resposta_fabio = resposta.choices[0].message.content
                st.session_state.mensagens.append({"role": "assistant", "content": resposta_fabio})
                salvar_historico(st.session_state.usuario, st.session_state.mensagens)
            except Exception as e:
                resposta_fabio = f"Erro na chamada  API: {str(e)}"
                st.session_state.mensagens.append({"role": "assistant", "content": resposta_fabio})
        for msg in st.session_state.mensagens:
            st.markdown(f"**{'Voc' if msg['role']=='user' else 'Fbio'}:** {msg['content']}")

    elif aba == " Produtos ESG":
        st.subheader(" Produtos ESG disponveis (exemplo)")
        st.markdown("Ainda no implementado com dados reais.")

    elif aba == " Dashboards":
        st.subheader(" Anlise ESG da Base de Clientes")

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.histogram(df, x="faixa_propensao", color="faixa_propensao",
                                title="Distribuio por Faixa de Propenso ESG",
                                color_discrete_sequence=["#FECB00"])
            fig1.update_traces(marker_line_color="black", marker_line_width=1)
            st.plotly_chart(fig1, use_container_width=True)

        with col2:
            fig2 = px.box(df, x="perfil_risco", y="propensao_esg", color="perfil_risco",
                          title="Propenso ESG por Perfil de Investidor",
                          color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig2, use_container_width=True)

        col3, col4 = st.columns(2)
        with col3:
            st.markdown("###  Top 5 - Baixa Propenso")
            st.dataframe(top_baixa[["nome", "propensao_esg", "perfil_risco"]], use_container_width=True)
        with col4:
            st.markdown("###  Top 5 - Mdia Propenso")
            st.dataframe(top_media[["nome", "propensao_esg", "perfil_risco"]], use_container_width=True)

    elif aba == " Recomendaes":
        st.subheader(" Recomendaes por Faixa de Propenso ESG")
        for _, cliente in df.iterrows():
            if cliente["faixa_propensao"] == "Baixa":
                acao = "Educar sobre ESG com contedo introdutrio."
            elif cliente["faixa_propensao"] == "Mdia":
                acao = "Apresentar produtos ESG e estimular interesse."
            else:
                acao = "Alocar diretamente em produtos ESG recomendados."
            st.info(f" {cliente['nome']} ({cliente['perfil_risco']})  {acao}")

    elif aba == " Alocao Inteligente":
        st.subheader(" Proposta de Alocao Inteligente com Produtos ESG")
        cliente_escolhido = st.selectbox("Selecione um cliente para anlise:", df["nome"])
        cliente_info = df[df["nome"] == cliente_escolhido].iloc[0]
        perfil = cliente_info["perfil_risco"]
        st.markdown(f"**Perfil de Investidor XP**: {perfil}")

        carteira_atual = {
            "Renda Fixa": 40 if perfil == "Conservador" else 25,
            "Fundos Multimercado": 30 if perfil == "Moderado" else 20,
            "Aes": 20 if perfil == "Agressivo" else 10,
            "Caixa": 10
        }

        st.markdown("###  Composio Atual da Carteira (Simulada)")
        st.write(carteira_atual)

        substituiveis = {
            "Renda Fixa": "XP Essencial ESG",
            "Fundos Multimercado": "XP ndice Sustentvel",
            "Aes": "XP Impacto Sustentvel"
        }

        st.markdown("###  Sugestes ESG com base nos ativos atuais:")
        nova_carteira = {}
        for ativo, perc in carteira_atual.items():
            if ativo in substituiveis:
                produto_esg = substituiveis[ativo]
                st.info(f" Substituir parte de **{ativo}** por **{produto_esg}** mantendo liquidez semelhante.")
                nova_carteira[produto_esg] = perc
            else:
                nova_carteira[ativo] = perc

        st.markdown("###  Proposta de Nova Carteira com Alocao ESG:")
        st.write(nova_carteira)
        st.success(" Proposta pronta para apresentao ao cliente.")
