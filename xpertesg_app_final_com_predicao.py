import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import os
import json

st.set_page_config(page_title="XPertESG", layout="wide")
COR_XP = "#FECB00"

# Dados simulados
from ModeloML import simular_base_clientes
from modelo_ml_integrado import carregar_modelo_pipeline
# Simular base e aplicar modelo preditivo
df = simular_base_clientes()

# Carrega pipeline treinado
modelo_pipeline = carregar_modelo_pipeline()
X = df.drop(columns=["nome"])

# Gera predições
df["propensao_esg"] = modelo_pipeline.predict_proba(X)[:, 1]
df["faixa_propensao"] = pd.cut(df["propensao_esg"], bins=[0, 0.4, 0.75, 1.0], labels=["Baixa", "Média", "Alta"])
df["esg_predito"] = modelo_pipeline.predict(X)
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
        "💡 Alocação Inteligente",
        "📢 Campanha"
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

            try:
                import openai
                client = openai.OpenAI(api_key=st.session_state.api_key)

                resposta = client.chat.completions.create(
                    model="gpt-3.5-turbo",
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
    
        df_rent = pd.read_csv("rentabilidade_fundos_esg_60m.csv")
    
        for p in produtos_esg:
            with st.expander(p["nome"]):
                st.markdown(f"**Tipo:** {p['tipo']}")
                st.markdown(f"**Risco:** {p['risco']}")
                st.markdown(f"**Taxa de administração:** {p['taxa']}")
                if "arquivo" in p:
                    st.markdown(f"[📄 Acessar Lâmina do Produto](./{p['arquivo']})")
                elif "lamina" in p:
                    st.markdown(f"[📄 Acessar Lâmina do Produto]({p['lamina']})")
    
                # Gráfico de rentabilidade acumulada e % retorno
                if p["nome"] in df_rent.columns:
                    df_plot = df_rent[["Data", p["nome"]]].copy()
                    df_plot["% Retorno"] = (df_plot[p["nome"]] / df_plot[p["nome"]].iloc[0] - 1) * 100
    
                    fig_rent = px.line(
                        df_plot,
                        x="Data",
                        y=[p["nome"], "% Retorno"],
                        title="Simulação de Rentabilidade Acumulada",
                        labels={
                            "value": "Valor",
                            "variable": "Métrica",
                            "Data": "Data"
                        },
                        line_shape="linear"
                    )
    
                    fig_rent.update_traces(line=dict(width=3))
                    fig_rent.for_each_trace(
                        lambda t: t.update(line_color="#FFFB00") if t.name == p["nome"] else t.update(line_color="#888888", line_dash="dot")
                    )
                    st.plotly_chart(fig_rent, use_container_width=True)
                else:
                    st.info("Simulação de rentabilidade não disponível para este fundo.")

    elif aba == "📈 Dashboards":
        st.subheader("📊 Análise ESG da Base de Clientes")
    
        col1, _ = st.columns(2)
        with col1:
            fig1 = px.histogram(df, x="faixa_propensao", color="faixa_propensao",
                                title="Distribuição por Faixa ESG",
                                color_discrete_sequence=["#FECB00"])
            fig1.update_traces(marker_line_color="black", marker_line_width=1)
            st.plotly_chart(fig1, use_container_width=True)
    
        col3, col4 = st.columns(2)
        with col3:
            st.markdown("### 🔝 Top 5 - Baixa Propensão")
            st.dataframe(top_baixa[["nome", "propensao_esg", "perfil_risco"]])
        with col4:
            st.markdown("### 🔝 Top 5 - Média Propensão")
            st.dataframe(top_media[["nome", "propensao_esg", "perfil_risco"]])
        
        st.markdown("### 🔝 Top 5 - Alta Propensão")
        st.dataframe(top_alta[["nome", "propensao_esg", "perfil_risco"]])
    
        # NOVOS GRÁFICOS E INSIGHTS ESG
    
        st.markdown("### ⏳ Clientes com ativos vencendo em até 30 dias")
        if "vence_em_dias" in df.columns:
            vencendo_30 = df[df["vence_em_dias"] <= 30]
            fig_vencendo = px.histogram(
                vencendo_30,
                x="faixa_propensao",
                color="perfil_risco",
                title="Faixa ESG dos Clientes com Ativos Próximos do Vencimento",
                color_discrete_sequence=px.colors.qualitative.Vivid
            )
            st.plotly_chart(fig_vencendo, use_container_width=True)
        else:
            st.warning("Coluna 'vence_em_dias' não encontrada na base.")
    
        st.markdown("### 📊 Clientes por Categoria de Produto Atual (simulada)")
        if "categoria_produto" in df.columns:
            fig_categoria = px.histogram(
                df,
                x="categoria_produto",
                color="faixa_propensao",
                title="Distribuição por Categoria de Produto",
                color_discrete_sequence=px.colors.qualitative.Prism
            )
            st.plotly_chart(fig_categoria, use_container_width=True)
        else:
            st.warning("Coluna 'categoria_produto' não encontrada na base.")
    
        st.markdown("### 🚫 Oportunidade ESG Inexplorada")
        if "produtos_esg" in df.columns:
            inexplorados = df[(df["faixa_propensao"] == "Alta") & (df["produtos_esg"] == 0)]
            st.metric(label="Clientes com Alta Propensão e Nenhum Produto ESG", value=len(inexplorados))
        else:
            st.warning("Coluna 'produtos_esg' não encontrada na base.")
    
        st.markdown("### 🔥 Heatmap ESG: Propensão x Categoria x Valor em Caixa")
        if all(col in df.columns for col in ["propensao_esg", "categoria_produto", "valor_em_caixa"]):
            heatmap_df = df.copy()
            heatmap_df["prop_bin"] = pd.cut(
                heatmap_df["propensao_esg"],
                bins=[0, 0.4, 0.75, 1.0],
                labels=["Baixa", "Média", "Alta"],
                include_lowest=True
            )
            heat = heatmap_df.groupby(["prop_bin", "categoria_produto"])["valor_em_caixa"].sum().reset_index()
            fig_heat = px.density_heatmap(
                heat,
                x="categoria_produto",
                y="prop_bin",
                z="valor_em_caixa",
                color_continuous_scale="Viridis",
                title="Heatmap ESG: Volume em Caixa por Propensão e Categoria"
            )
            st.plotly_chart(fig_heat, use_container_width=True)
        else:
            st.warning("Colunas necessárias para o Heatmap não estão completas.")

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
    
        # Seleção de cliente da base
        cliente_selecionado = st.selectbox("Selecione um cliente:", df["nome"])
        cliente_info = df[df["nome"] == cliente_selecionado].iloc[0]
        perfil = cliente_info["perfil_risco"]
        st.markdown(f"**Perfil de Investidor XP:** {perfil}")
    
        # Definições de alocação padrão por perfil
        if perfil == "Conservador":
            carteira_base = {
                "Renda Fixa": 50000,
                "Multimercado": 30000,
                "Caixa": 20000
            }
        elif perfil == "Moderado":
            carteira_base = {
                "Multimercado": 40000,
                "Renda Fixa": 30000,
                "ETF": 30000
            }
        else:  # Agressivo
            carteira_base = {
                "Renda Variável": 40000,
                "ETF": 35000,
                "Multimercado": 25000
            }
    
        # Produtos ESG disponíveis
        produtos_esg = [
            {"nome": "Fundo XP Essencial ESG", "categoria": "Renda Fixa", "risco": 3},
            {"nome": "Pandhora ESG Prev", "categoria": "Multimercado", "risco": 7},
            {"nome": "ETF XP Sustentável", "categoria": "ETF", "risco": 10},
            {"nome": "Fundo XP Verde Ações", "categoria": "Renda Variável", "risco": 15}
        ]
    
        # Simular substituições parciais
        carteira_recomendada = []
        substituicoes = []
    
        for categoria, valor in carteira_base.items():
            if categoria in ["Caixa"]:
                carteira_recomendada.append({"Produto": categoria, "Valor": valor})
                continue
    
            esg_produto = next((p for p in produtos_esg if p["categoria"] == categoria), None)
            if esg_produto:
                valor_esg = valor * 0.5
                valor_tradicional = valor * 0.5
                carteira_recomendada.append({"Produto": f"{categoria} Tradicional", "Valor": valor_tradicional})
                carteira_recomendada.append({"Produto": f"{esg_produto['nome']}", "Valor": valor_esg})
                substituicoes.append({
                    "Categoria": categoria,
                    "ESG Sugerido": esg_produto["nome"],
                    "Porcentagem ESG": "50%",
                    "Motivo": "Risco compatível e disponível ESG na mesma classe"
                })
            else:
                carteira_recomendada.append({"Produto": categoria, "Valor": valor})
    
        # Gráficos
        col1, col2 = st.columns(2)
    
        with col1:
            df_atual = pd.DataFrame({"Produto": list(carteira_base.keys()), "Valor": list(carteira_base.values())})
            fig1 = px.pie(df_atual, names='Produto', values='Valor', title="Carteira Atual por Categoria")
            st.plotly_chart(fig1, use_container_width=True)
    
        with col2:
            df_nova = pd.DataFrame(carteira_recomendada)
            fig2 = px.pie(df_nova, names='Produto', values='Valor', title="Carteira Recomendada com ESG")
            st.plotly_chart(fig2, use_container_width=True)
    
        # Tabela de substituições
        if substituicoes:
            st.markdown("### 📌 Substituições Recomendadas")
            st.dataframe(pd.DataFrame(substituicoes))
        else:
            st.info("Nenhuma substituição ESG recomendada no momento.")
            
    elif aba == "📊 Propensão ESG":
        st.subheader("📊 Propensão ESG dos Clientes")

        st.markdown("### 🔍 Tabela com predições")
        st.dataframe(df[["nome", "perfil_risco", "propensao_esg", "faixa_propensao", "esg_predito"]])

        st.markdown("### 📊 Distribuição por Faixa")
        fig = px.histogram(df, x="faixa_propensao", color="faixa_propensao", color_discrete_sequence=["#FECB00"])
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("### 🔍 Filtrar por Perfil de Risco")
        perfil = st.selectbox("Selecione um perfil:", df["perfil_risco"].unique())
        filtrado = df[df["perfil_risco"] == perfil]
        st.dataframe(filtrado[["nome", "propensao_esg", "faixa_propensao", "esg_predito"]])

    elif aba == "📢 Campanha":
        st.subheader("📢 Campanha de Alocação ESG")
    
        # Simular histórico de alocação do assessor e da média XP
        datas = pd.date_range(end=pd.Timestamp.today(), periods=12, freq='M')
        aloc_assessor = np.cumsum(np.random.randint(10000, 50000, size=12))
        aloc_xp = np.cumsum(np.random.randint(15000, 40000, size=12))
    
        df_campanha = pd.DataFrame({
            "Data": datas,
            "Assessor": aloc_assessor,
            "Média XP": aloc_xp
        })
    
        # Gráfico de linha: evolução individual
        st.markdown("### 📈 Alocação Acumulada ao Longo do Tempo")
        fig_crescimento = px.line(
            df_campanha,
            x="Data",
            y="Assessor",
            title="Alocação ESG - Assessor",
            markers=True,
            labels={"Assessor": "Valor Acumulado (R$)"},
            line_shape="linear"
        )
        fig_crescimento.update_traces(line=dict(color="#FFFF00", width=3))

        st.plotly_chart(fig_crescimento, use_container_width=True)
    
        # Gráfico comparativo: assessor vs XP
        st.markdown("### ⚖️ Comparativo com Média da XP")
        total_assessor = aloc_assessor[-1]
        total_xp = aloc_xp[-1]
    
        fig_barra = px.bar(
            x=["Assessor", "Média XP"],
            y=[total_assessor, total_xp],
            labels={"x": "Origem", "y": "Valor Total Alocado"},
            color=["Assessor", "Média XP"],
            title="Total Alocado no Ano"
        )
        st.plotly_chart(fig_barra, use_container_width=True)
    
        # Estatísticas gerais
        st.markdown("### 🧾 Estatísticas da Campanha")
        st.metric("Total Alocado pelo Assessor", f"R$ {total_assessor:,.0f}")
        st.metric("Média de Alocação XP", f"R$ {total_xp:,.0f}")
    
        # Sugestões de gamificação futura
        st.markdown("### 🕹️ Ideias para Futuras Gamificações")
        st.markdown("- 🏆 **Ranking de Assessores por Alocação ESG**")
        st.markdown("- 🎯 **Metas Mensais com Recompensas**")
        st.markdown("- 🥇 **Badges como 'Top ESG' ou '100% Verde'**")
        st.markdown("- 📅 **Missões Semanais para Diversificação**")
        st.markdown("- 💰 **Simulação de Pontos ou Cashback Interno**")
