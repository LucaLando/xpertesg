
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
df["faixa_propensao"] = pd.cut(df["propensao_esg"], bins=[0, 0.4, 0.75, 1.0], labels=["Baixa", "Média", "Alta"])

top_baixa = df[df["faixa_propensao"] == "Baixa"].nlargest(5, "propensao_esg")
top_media = df[df["faixa_propensao"] == "Média"].nlargest(5, "propensao_esg")
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

st.sidebar.markdown("## 👤 Login do Assessor")
usuario_input = st.sidebar.text_input("Digite seu nome de usuário")
if st.sidebar.button("Entrar") and usuario_input:
    st.session_state.usuario = usuario_input
    st.session_state.mensagens = carregar_historico(usuario_input)
    st.success(f"Bem-vindo, {usuario_input}!")

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

    elif aba == "📦 Produtos ESG":
        st.subheader("🌱 Produtos ESG disponíveis")
        produtos_esg = [
            {"nome": "Fundo XP Essencial ESG", "tipo": "Renda Fixa", "risco": "Baixo", "taxa": "0,9% a.a.", "arquivo": "lamina_xp_essencial.pdf"},
            {"nome": "ETF XP Sustentável", "tipo": "ETF", "risco": "Médio", "taxa": "0,3% a.a.", "arquivo": "lamina_xp_etf.pdf"},
            {"nome": "Fundo XP Verde Ações", "tipo": "Ações", "risco": "Alto", "taxa": "1,2% a.a.", "arquivo": "lamina_xp_verde.pdf"},
            {"nome": "Fundo XP Impacto Social", "tipo": "Multimercado", "risco": "Médio", "taxa": "1,0% a.a.", "arquivo": "lamina_xp_impacto.pdf"},
            {
                "nome": "Trend ESG Global Dólar FIM",
                "tipo": "Multimercado Internacional",
                "risco": "Médio",
                "taxa": "0,5% a.a.",
                "descricao": "Fundo indexado que investe em ETFs internacionais com foco em empresas reconhecidas por boas práticas ESG.",
                "lamina": "https://conteudos.xpi.com.br/previdencia-privada/relatorios/pandhora-esg-prev-o-novo-fundo-de-acoes-da-pandhora/"
            },
            {
                "nome": "Pandhora ESG Prev",
                "tipo": "Previdência – Ações Long Bias",
                "risco": "Alto",
                "taxa": "1,5% a.a.",
                "descricao": "Fundo de previdência com estratégia Long Bias e filtro ESG, combinando ações, ativos macro e exposição internacional.",
                "lamina": "https://conteudos.xpi.com.br/previdencia-privada/relatorios/pandhora-esg-prev-o-novo-fundo-de-acoes-da-pandhora/"
            },
            {
                "nome": "JGP Ações 100 Prev XP Seguros FIC FIA",
                "tipo": "Previdência – Ações",
                "risco": "Alto",
                "taxa": "2,0% a.a.",
                "descricao": "Fundo de ações com foco em empresas sustentáveis, disponível na plataforma de previdência da XP.",
                "lamina": "https://conteudos.xpi.com.br/previdencia-privada/jgp-acoes-100-prev-xp-seg-fic-fia/"
            }
        ]
        for p in produtos_esg:
            with st.expander(p["nome"]):
                st.markdown(f"**Tipo:** {p['tipo']}")
                st.markdown(f"**Risco:** {p['risco']}")
                st.markdown(f"**Taxa de administração:** {p['taxa']}")
                if "arquivo" in p:
                    st.markdown(f"[📄 Acessar Lâmina do Produto](./{p['arquivo']})")
                elif "lamina" in p:
                    st.markdown(f"[📄 Acessar Lâmina do Produto]({p['lamina']})")

    elif aba == "📈 Dashboards":
        st.subheader("📊 Análise ESG da Base de Clientes")
        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.histogram(df, x="faixa_propensao", color="faixa_propensao",
                                title="Distribuição por Faixa ESG",
                                color_discrete_sequence=["#FECB00"])
            fig1.update_traces(marker_line_color="black", marker_line_width=1)
            st.plotly_chart(fig1, use_container_width=True)
        with col2:
            fig2 = px.box(df, x="perfil_risco", y="propensao_esg", color="perfil_risco",
                          title="Propensão ESG por Perfil",
                          color_discrete_sequence=px.colors.qualitative.Safe)
            st.plotly_chart(fig2, use_container_width=True)
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### 🔝 Top 5 - Baixa Propensão")
            st.dataframe(top_baixa[["nome", "propensao_esg", "perfil_risco"]])
        with col4:
            st.markdown("### 🔝 Top 5 - Média Propensão")
            st.dataframe(top_media[["nome", "propensao_esg", "perfil_risco"]])
        st.markdown("### 🔝 Top 5 - Alta Propensão")
        st.dataframe(top_alta[["nome", "propensao_esg", "perfil_risco"]])

    elif aba == "📌 Recomendações":
        st.subheader("📌 Recomendações por Faixa ESG")
        for _, cliente in df.iterrows():
            if cliente["faixa_propensao"] == "Baixa":
                acao = "Educar sobre ESG com conteúdo introdutório."
            elif cliente["faixa_propensao"] == "Média":
                acao = "Apresentar produtos ESG e estimular interesse."
            else:
                acao = "Alocar diretamente em produtos ESG recomendados."
            st.info(f"👤 {cliente['nome']} ({cliente['perfil_risco']}) → {acao}")

    elif aba == "💡 Alocação Inteligente":
        st.subheader("💡 Alocação Inteligente com ESG")
    
        # Seleção de cliente real da base
        cliente_selecionado = st.selectbox("Selecione um cliente:", df["nome"])
        cliente_info = df[df["nome"] == cliente_selecionado].iloc[0]
        perfil = cliente_info["perfil_risco"]
    
        st.markdown(f"**Perfil de Investidor XP:** {perfil}")
    
        # Simula carteira com base no perfil de risco
        if perfil == "Conservador":
            carteira_atual = [
                {"produto": "Tesouro IPCA 2026", "categoria": "Renda Fixa", "risco": 3, "valor": 50000, "vence_em_dias": 30},
                {"produto": "Fundo Conservador XP", "categoria": "Multimercado", "risco": 5, "valor": 30000, "vence_em_dias": 150},
                {"produto": "Caixa", "categoria": "Caixa", "risco": 1, "valor": 20000, "vence_em_dias": 0}
            ]
        elif perfil == "Moderado":
            carteira_atual = [
                {"produto": "Fundo Alpha Multimercado", "categoria": "Multimercado", "risco": 7, "valor": 40000, "vence_em_dias": 180},
                {"produto": "Tesouro Selic", "categoria": "Renda Fixa", "risco": 3, "valor": 30000, "vence_em_dias": 60},
                {"produto": "ETF BRAX11", "categoria": "ETF", "risco": 10, "valor": 30000, "vence_em_dias": 365}
            ]
        else:  # Agressivo
            carteira_atual = [
                {"produto": "Fundo RV XP Tech", "categoria": "Renda Variável", "risco": 15, "valor": 40000, "vence_em_dias": 90},
                {"produto": "ETF NASD11", "categoria": "ETF", "risco": 10, "valor": 35000, "vence_em_dias": 120},
                {"produto": "Fundo Macro XP", "categoria": "Multimercado", "risco": 7, "valor": 25000, "vence_em_dias": 45}
            ]
    
        # Produtos ESG disponíveis
        produtos_esg = [
            {"nome": "Fundo XP Essencial ESG", "categoria": "Renda Fixa", "risco": 3},
            {"nome": "Pandhora ESG Prev", "categoria": "Multimercado", "risco": 7},
            {"nome": "ETF XP Sustentável", "categoria": "ETF", "risco": 10},
            {"nome": "Fundo XP Verde Ações", "categoria": "Renda Variável", "risco": 15}
        ]
    
        # Avaliação de substituições ESG
        substituicoes = []
        nova_carteira = []
    
        for ativo in carteira_atual:
            substituido = False
            for esg in produtos_esg:
                if esg["categoria"] == ativo["categoria"] and esg["risco"] == ativo["risco"] and ativo["vence_em_dias"] <= 90:
                    substituicoes.append({
                        "Produto Atual": ativo["produto"],
                        "Categoria": ativo["categoria"],
                        "Risco": ativo["risco"],
                        "Produto ESG Sugerido": esg["nome"],
                        "Motivo": "Vencimento próximo e risco compatível"
                    })
                    nova_carteira.append({"Produto": esg["nome"], "Valor": ativo["valor"]})
                    substituido = True
                    break
            if not substituido:
                nova_carteira.append({"Produto": ativo["produto"], "Valor": ativo["valor"]})
    
        # Gráficos de pizza
        col1, col2 = st.columns(2)
        with col1:
            df_atual = pd.DataFrame([{"Produto": a["produto"], "Valor": a["valor"]} for a in carteira_atual])
            fig1 = px.pie(df_atual, names='Produto', values='Valor', title="Carteira Atual")
            st.plotly_chart(fig1, use_container_width=True)
    
        with col2:
            df_nova = pd.DataFrame(nova_carteira)
            fig2 = px.pie(df_nova, names='Produto', values='Valor', title="Carteira Recomendada com ESG")
            st.plotly_chart(fig2, use_container_width=True)
    
        # Tabela de substituições
        if substituicoes:
            st.markdown("### 📌 Substituições Recomendadas")
            df_subs = pd.DataFrame(substituicoes)
            st.dataframe(df_subs)
        else:
            st.info("Nenhuma substituição ESG recomendada no momento com base na carteira e vencimentos.")
