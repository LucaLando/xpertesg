import numpy as np
import streamlit as st
import pandas as pd
import plotly.express as px
import openai
import os
import json
import plotly.graph_objects as go
import re

# 1) PAGE CONFIGURATIONS — SEMPRE em primeiro lugar
st.set_page_config(page_title="XPertESG", layout="wide")

# 2) CABEÇALHO
# Supondo que você tenha 'Cabeçalho.png' na raiz do repo (ou ajuste o caminho)

# 3) O resto do seu app...
if "usuario" not in st.session_state:
    st.session_state.usuario = ""

COR_XP = "#FECB00"
ALTO_ESG = "#1b8e40"
MEDIO_ESG = "#3e6049"
BAIXO_ESG = "#031d44"
PROD_ESG = "#0a762d"
TRAD1 = "e0e0e0"
TRAD2 = "031D44"
TRAD3 = "04395E"

# Função para simular carteira de cada cliente
def simulate_portfolios(df):
    categories = ["Caixa", "Renda Fixa", "Multimercado", "Renda Variável", "ETF"]
    totais = np.random.uniform(50000, 500000, size=len(df)).round(2)
    portfolios = []
    for total in totais:
        props = np.random.dirichlet(np.ones(len(categories)), size=1)[0]
        port = {cat: float((total * p).round(2)) for cat, p in zip(categories, props)}
        portfolios.append(port)
    df["ValorTotalCarteira"] = totais
    df["ValorEmCaixa"] = [p["Caixa"] for p in portfolios]
    df["ValorAlocadoESG"] = [round(total - vc, 2) for total, vc in zip(totais, df["ValorEmCaixa"])]
    df["Carteira"] = portfolios
    return df
# Dados simulados
df = pd.read_csv("base5_clientes_esg10000.csv")

# Mapear códigos de risco para nomes legíveis
mapa_perfil = {0: "Conservador", 1: "Moderado", 2: "Agressivo"}
df["PerfilRisco"] = df["PerfilRisco"].map(mapa_perfil)
# Garante colunas mínimas para o gráfico de dispersão


# 🧾 Adicionar nome fictício com base no gênero
nomes_masculinos = [
    "Lucas", "João", "Pedro", "Rafael", "Gustavo", "Matheus", "Thiago", "Bruno", "Felipe", "André",
    "Carlos", "Daniel", "Henrique", "Eduardo", "Leonardo", "Gabriel", "Caio", "Marcelo", "Igor", "Victor",
    "Renato", "Rodrigo", "Alexandre", "Vitor", "Diego", "Fernando", "Ricardo", "Samuel", "Luan", "Fábio",
    "Paulo", "Otávio", "Hugo", "Antônio", "Jonathan", "Roberto", "Vinicius", "Murilo", "Leandro", "Jorge",
    "Elias", "Juliano", "Marcos", "Raul", "Estevão", "Heitor", "Nelson", "Brayan", "Caetano", "Wallace",
    "Danilo", "Adriano", "Júnior", "Alfredo", "Valter", "Nathan", "Wesley", "Jeferson", "Maicon", "Ezequiel",
    "Cristiano", "William", "Matias", "Eliseu", "Luciano", "Flávio", "Rogério", "Saulo", "Sérgio", "Davi",
    "Érico", "Iago", "Emanuel", "Luiz", "Giovani", "Tiago", "Édson", "Silas", "Moisés", "Afonso",
    "Douglas", "Washington", "Breno", "Joabe", "Geovani", "Ruan", "Nicolas", "Cláudio", "Alex", "Lázaro",
    "Adriel", "Milton", "Rômulo", "Israel", "Anderson", "Tales", "Valmir", "Eron"
]

nomes_femininos = [
    "Ana", "Beatriz", "Camila", "Daniela", "Eduarda", "Fernanda", "Gabriela", "Helena", "Isabela", "Juliana",
    "Karen", "Larissa", "Mariana", "Natália", "Olívia", "Patrícia", "Queila", "Renata", "Sabrina", "Tatiane",
    "Úrsula", "Vitória", "Wendy", "Ximena", "Yasmin", "Zuleika", "Aline", "Bianca", "Carolina", "Débora",
    "Elaine", "Fabiana", "Giovana", "Heloísa", "Ingrid", "Jéssica", "Kátia", "Letícia", "Michele", "Nicole",
    "Priscila", "Raquel", "Simone", "Tainá", "Vanessa", "Waleska", "Yara", "Zélia", "Amélia", "Bárbara",
    "Clarissa", "Denise", "Estela", "Flávia", "Graziele", "Hortência", "Ione", "Joana", "Kelly", "Lilian",
    "Mônica", "Noemi", "Odete", "Paloma", "Rafaela", "Sônia", "Tereza", "Valéria", "Wilma", "Zilda",
    "Andressa", "Cíntia", "Dandara", "Emanuelle", "Francine", "Gláucia", "Hermínia", "Ivone", "Jacira", "Késia",
    "Luzia", "Marta", "Nadja", "Orlanda", "Penélope", "Regina", "Sheila", "Talita", "Vera", "Zenaide",
    "Aurora", "Celina", "Dalva", "Eliana", "Fabíola", "Gislaine", "Hilda", "Iraci", "Jacqueline", "Lúcia"
]

import random

def gerar_nome(genero):
    if genero == "Masculino":
        return random.choice(nomes_masculinos)
    elif genero == "Feminino":
        return random.choice(nomes_femininos)
    else:
        return "Cliente XP"


# Classificar propensão manualmente
def classificar_faixa(p):
    if p <= 0.40:
        return "Baixa"
    elif p <= 0.74:
        return "Média"
    else:
        return "Alta"

df["faixa_propensao"] = df["propensao_esg"].apply(classificar_faixa)

# Aplica nomes com base no gênero
nomes = nomes_masculinos + nomes_femininos
df["nome"] = [random.choice(nomes) for _ in range(len(df))]
df = simulate_portfolios(df)



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


# Configuração inicial da página

# --- Página de Login (Splash Screen) ---
if not st.session_state.usuario:
    # Duas colunas: esquerda (login + texto), direita (branding)
    col1, col2 = st.columns([1, 2], gap="large")

    with col1:
        # Logo principal
        st.image("XPert2.PNG", use_container_width=True)
        st.markdown("## Login do Assessor")

        # Campo de entrada do usuário
        usuario_input = st.text_input("Digite seu nome de usuário")
        if st.button("Entrar") and usuario_input:
            st.session_state.usuario = usuario_input
            st.rerun()

        # Texto de boas-vindas / missão ESG
        st.markdown(
            """
            Acreditamos que os investimentos também podem ser ferramentas que geram valor para a sociedade e para o meio ambiente, quando
            realizados de forma consciente e responsável. Queremos ampliar o conhecimento do mercado sobre a agenda ESG, e colocá-la no
            centro dos modelos de negócio e do processo de tomada de decisão.
            """
        )


    with col2:
        # Slogan principal
        st.markdown(
            "<h1 style='line-height:1.2; margin-bottom:1rem;'>"
            "SÓ TRANSFORMA O FUTURO<br>QUEM INVESTE NO PRESENTE."
            "</h1>",
            unsafe_allow_html=True
        )
    
        # Espaço para dar altura ao container
        st.markdown("<div style='height:200px;'></div>", unsafe_allow_html=True)
    
        # Texto “Em que futuro…” posicionado no canto inferior direito deste col2
        st.markdown(
            """
            <div style="position: relative; width: 100%; height: 100px;">
              <h3 style="
                  position: absolute;
                  bottom: 0;
                  right: 0;
                  color: #1b8e40;
                  font-size: 2rem;
                  line-height: 1.2;
                  margin: 0;
              ">
                Em que futuro você<br>quer investir?
              </h3>
            </div>
            """,
            unsafe_allow_html=True,
        )
    # ----------------------------------------------

    # Interrompe aqui para que o restante do app só seja executado após login
    st.stop()

# Cabeçalho exibido somente após login
st.image("Cabeçalho.png", use_container_width=True)
    
# Logo na barra lateral
st.sidebar.image("XPert2.PNG", use_container_width=True)

st.sidebar.markdown("##  Login do Assessor")
usuario_input = st.sidebar.text_input("Digite seu nome de usuário")
if st.sidebar.button("Entrar") and usuario_input:
    st.session_state.usuario = usuario_input
    st.session_state.mensagens = carregar_historico(usuario_input)

if st.session_state.usuario:
    aba = st.sidebar.radio(" Escolha uma seção:", [
        " Clientes",
        " Chat com Fábio",
        " Produtos ESG",
        " Dashboard",
        " Alocação Inteligente",
        " Campanha"
    ])

    if aba == " Clientes":
        st.title(" Clientes")
        st.dataframe(df, use_container_width=True)

    elif aba == " Chat com Fábio":
        subtab1, subtab2 = st.tabs(["Conversa", "Portal Informações ESG"])
    with subtab1:
        try:
                st.title(" Fábio – Assistente Virtual ESG")
            
                # ——— 1a) Uploads opcionais ———
                uploaded_clients = st.file_uploader(
                    "Faça upload da base de clientes (CSV)",
                    type=["csv"],
                    help="Selecione o arquivo CSV contendo os dados de clientes ESG."
                )
                uploaded_products = st.file_uploader(
                    "Faça upload da lista de produtos ESG (opcional)",
                    type=["csv", "json"],
                    help="Se você tiver um CSV/JSON com os produtos ESG, faça o upload aqui."
                )
            
                # ——— 1) Configuração da chave da API ———
                if "api_key" not in st.session_state:
                    st.session_state.api_key = ""
                with st.expander(" Configurar Chave da API OpenAI", expanded=True):
                    st.session_state.api_key = st.text_input(
                        "Cole aqui sua API Key:", type="password", key="openai_api_key"
                    )
            
                # ——— 2) Histórico de mensagens ———
                if "mensagens" not in st.session_state:
                    st.session_state.mensagens = []
            
                # ——— 3) Construção de df_clients já contendo a coluna 'Carteira' ———
                # (a) Caso não tenha upload, usamos o DataFrame global 'df' que já passou por simulate_portfolios()
                if uploaded_clients is None:
                    df_clients = df.copy()
                else:
                    # (b) Se houve upload de CSV puro, carregamos, mapeamos e simulamos a carteira
                    try:
                        df_raw = pd.read_csv(uploaded_clients)
                    except Exception as e:
                        st.error(f"Erro ao ler arquivo de clientes: {e}")
                        st.stop()
            
                    # Mapeia 'PerfilRisco' para texto, se numérico
                    if "PerfilRisco" in df_raw.columns:
                        df_raw["PerfilRisco"] = df_raw["PerfilRisco"].map(mapa_perfil).fillna(df_raw["PerfilRisco"])
            
                    # Gera a carteira e demais campos usando simulate_portfolios()
                    df_clients = simulate_portfolios(df_raw)
            
                    # Cria coluna 'faixa_propensao' caso exista 'propensao_esg'
                    if "propensao_esg" in df_clients.columns:
                        df_clients["faixa_propensao"] = df_clients["propensao_esg"].apply(classificar_faixa)
            
                    # Se não houver coluna 'nome', gera nomes fictícios
                    if "nome" not in df_clients.columns:
                        df_clients["nome"] = [random.choice(nomes_masculinos + nomes_femininos) for _ in range(len(df_clients))]
            
                    # Mapeia 'PerfilRisco' para texto, se necessário
                    if "PerfilRisco" in df_clients.columns:
                        df_clients["PerfilRisco"] = df_clients["PerfilRisco"].map(mapa_perfil).fillna(df_clients["PerfilRisco"])
            
                # ——— 4) Carrega lista de produtos ESG se enviado externamente ———
                if uploaded_products is not None:
                    try:
                        if uploaded_products.name.lower().endswith(".csv"):
                            df_products_externo = pd.read_csv(uploaded_products)
                        else:
                            df_products_externo = pd.read_json(uploaded_products)
                        produtos_esg = df_products_externo.to_dict(orient="records")
                    except Exception as e:
                        st.error(f"Erro ao ler arquivo de produtos ESG: {e}")
                        produtos_esg = None
                else:
                    produtos_esg = None
            
                # ——— 5) Verificação de colunas obrigatórias em df_clients ———
                id_col         = "ID"
                age_col        = "Idade"
                risk_col       = "PerfilRisco"
                engagement_col = "EngajamentoESG"
                prop_col       = "propensao_esg"
                carteira_col   = "Carteira"
            
                for c in (id_col, age_col, risk_col, engagement_col, prop_col, carteira_col):
                    if c not in df_clients.columns:
                        st.error(f"Coluna obrigatória não encontrada no CSV: {c}")
                        st.stop()
            
                # ——— 6) Prompt do sistema (atualizado com faixas de propensão e macro) ———
                SYSTEM_PROMPT = {
                    "role": "system",
                    "content": """
            Você é o Fábio, um assistente virtual especializado em produtos de investimento ESG da XP Inc., voltado exclusivamente para assessores de investimentos da própria XP.
            
            Seu papel é fornecer orientação técnica, estratégica e educacional sobre a alocação de capital em produtos disponíveis na XP, considerando sempre:
            - A carteira de produtos ESG da XP.
            - O perfil de risco do cliente.
            - O grau de propensão ESG do cliente (quando informado), categorizado assim:
              • Propensão ESG baixa: até 0,40 (inclusive).
              • Propensão ESG média: de 0,41 até 0,75 (inclusive).
              • Propensão ESG alta: a partir de 0,76.
            - As diretrizes regulatórias e reputacionais da XP Inc.
            
            🧠 CONHECIMENTO E COMPORTAMENTO
            Você é especialista em:
            • Fundos ESG (FIA, FIP, FIE, FIDC ESG etc.)
            • Debêntures e COEs com propósito ESG
            • Certificados como CPR Verde e créditos de carbono
            • Ativos ambientais (Green Bonds, Marketplaces de Carbono)
            • Critérios ESG usados pela XP (frameworks SASB, ICVM 59, Taxonomia Verde)
            • Alinhamento a padrões internacionais (ODS/Agenda 2030, Selo B, índices CSA da S&P, CDP etc.)
            • Relação entre desempenho de fundos e contexto macroeconômico (SELIC, inflação, cenário político, taxas de juros)
            
            Você se comunica com linguagem empresarial, técnica e confiável, em linha com o tom institucional da XP Inc.
            
            **Instruções de uso de contexto e estilo**
            - Ao receber dados do cliente (ID, nome, idade, perfil de risco, engajamento ESG, propensão ESG, carteira), use-os imediatamente na resposta.
            - Nunca use frases de transição (“um momento”, “vou verificar”) ou peça para consultar outra área.
            - Se faltar algum campo, mencione apenas o nome do campo ausente.
            - Utilize a coluna “Carteira” da base para responder sobre composição de portfólio.
            - Em todas as comunicações, **SEM-PRE** destaque os retornos financeiros históricos e expectativas futuras dos fundos.
            - Inclua análises comparativas entre o desempenho do fundo e indicadores macroeconômicos:  
              • Exemplo: “Se um fundo rendeu 16% no último ano e a SELIC está em 14,75%, isso é considerado bom desempenho.”  
              • Cite também inflação, prazos, volatilidade e outros fatores macro quando relevante.
            
            **Definição de estratégias de abordagem por faixa de propensão ESG**
            1. **Propensão ESG baixa (até 0,40)**  
               - Não enfatize a temática ESG ou selos verdes: apresente o produto como um fundo de investimento tradicional.  
               - Foque em:  
                 1. Rentabilidade histórica e expectativa de retorno absoluto e relativo (CDI/SELIC).  
                 2. Perfil de risco, volatilidade e prazo.  
                 3. Liquidez e prazos de resgate.  
                 4. Taxas de administração e performance.  
                 5. Diversificação.  
               - Exemplo de frase:  
                 “Este fundo rendeu 12% nos últimos 12 meses, superando o CDI de 9,5% no mesmo período, com volatilidade controlada em 6% ao ano.”
            
            2. **Propensão ESG média (0,41 a 0,75)**  
               - Apresente ESG de forma equilibrada: mencione práticas de sustentabilidade, mas priorize retorno financeiro.  
               - Destaque:  
                 1. Rating ESG ou menção breve a empresas responsáveis.  
                 2. Valor agregado no médio/longo prazo (menor risco reputacional).  
                 3. Performance comparada a benchmarks (CDI, IBOV).  
               - Exemplo de frase:  
                 “Este fundo investe em empresas que atendem a padrões ESG reconhecidos, mas tenha em vista que o principal ponto é a performance: ele rendeu 14% no último ano, frente a 10% do CDI, com liquidez de D+1.”
            
            3. **Propensão ESG alta (acima de 0,76)**  
               - Enriquecer a conversa com detalhes de impacto ESG:  
                 1. Critérios de seleção (SASB, ICVM 59, Taxonomia Verde).  
                 2. Selos ou certificações (Selo B, Índice ESG da S&P).  
                 3. Impacto social/ambiental (carbono, green bonds).  
               - Ainda assim, mantenha o retorno financeiro como ponto central:  
                 1. “Apesar de forte viés ESG, entregou 13% no último ano, contra 11% do CDI.”  
                 2. Compare com SELIC e outros indicadores macroeconômicos:  
                    - “Com a SELIC em 14,75%, esse retorno líquido de 13% mostra competitividade, considerando taxa de 1% a.a.”  
               - Exemplo de frase:  
                 “Este fundo investe em empresas com compromisso ESG de nível 1 ou 2, com Selo B, e entregou 15% nos últimos 12 meses, superando a SELIC de 14,75%.”
            
            🔍 **FONTES E ATUALIZAÇÕES**  
            - Você pode acessar sites oficiais da XP para dados atualizados de cada fundo:  
              • https://conteudos.xpi.com.br/esg/  
              • https://www.xpi.com.br
            
            📂 **BASES DISPONÍVEIS**  
            - Você possui acesso ao DataFrame `df_clients`, que já contém a coluna `Carteira` gerada por `simulate_portfolios()`.
            
            🎯 **ORIENTAÇÃO AO ASSESSOR**  
            - Nunca fale diretamente com o cliente final; dirija-se ao assessor.  
            - Oriente com dados técnicos, não opiniões pessoais.  
            - Para cada faixa de propensão, ajuste o discurso conforme descrito, mas **sempre** apresente o retorno financeiro como principal argumento.
            
            🔧 **SUGESTÕES TÉCNICAS**  
            - Ativar Browser Tool (se disponível).  
            - Atualizar base de clientes a cada rodada.  
            - Manter threads fixos por assessor (usar `thread_id`).  
            - Logar interações (timestamp, ID do assessor, input e resposta).  
            - Fallback: “Produto não consta na base atual. Consulte a plataforma oficial da XP.”
            """
                }
            
                # ——— 7) Exibe todo o histórico antes do input ———
                for msg in st.session_state.mensagens:
                    st.chat_message(msg["role"]).write(msg["content"])
            
                # ——— 8) Captura o input do usuário ———
                user_input = st.chat_input("Digite sua pergunta para o Fábio:")
            
                # ——— 9) Se o usuário digitou algo, processa ———
                if user_input:
                    # a) Exibe e armazena a pergunta
                    st.chat_message("user").write(user_input)
                    st.session_state.mensagens.append({"role": "user", "content": user_input})
            
                    # b) Extrai contexto do cliente, incluindo 'Carteira'
                    client_context = None
                    m = re.search(r"cliente\s+(\d+)", user_input, flags=re.IGNORECASE)
                    if m:
                        cli_id = int(m.group(1))
                        rec = df_clients.loc[df_clients[id_col] == cli_id]
                        if not rec.empty:
                            rec = rec.iloc[0]
                            client_context = (
                                f"DADOS DO CLIENTE {cli_id}:\n"
                                f"• Idade: {rec[age_col]}\n"
                                f"• Perfil de risco: {rec[risk_col]}\n"
                                f"• Engajamento ESG: {rec[engagement_col]}\n"
                                f"• Propensão ESG: {rec[prop_col]}\n"
                                f"• Carteira: {rec[carteira_col]}\n"
                            )
            
                    # c) Monta as mensagens e chama a API
                    messages = [SYSTEM_PROMPT]
                    if client_context:
                        messages.append({"role": "system", "content": client_context})
                    messages += st.session_state.mensagens
            
                    openai.api_key = st.session_state.api_key
                    try:
                        response = openai.chat.completions.create(
                            model="gpt-3.5-turbo",
                            messages=messages,
                            temperature=0.7,
                            max_tokens=700
                        )
                        fabio_reply = response.choices[0].message.content
                    except Exception as e:
                        fabio_reply = f"Erro na chamada à API: {e}"
            
                    # d) Exibe e salva a resposta
                    st.chat_message("assistant").write(fabio_reply)
                    st.session_state.mensagens.append({"role": "assistant", "content": fabio_reply})
            
                    # e) Persiste histórico
                    salvar_historico(st.session_state.usuario, st.session_state.mensagens)    
        except Exception as e:
            st.error(f"Erro interno no Chat com Fábio: {e}")

    
        with subtab2:
            st.title(" Portal de Informações ESG")
            if "api_key" not in st.session_state:
                st.warning("Configure a API Key na aba Conversa")
            else:
                # Prompt pré-definido para informações ESG
                prompt = """Forneça uma análise econômica comparativa entre produtos ESG comercializados na XP desde 2023 e investimentos tradicionais, incluindo rentabilidade média líquida, custo de oportunidade, CAPM e principais indicadores de desempenho."""
                messages = [SYSTEM_PROMPT, {"role": "user", "content": prompt}]
                openai.api_key = st.session_state.api_key
                try:
                    response = openai.chat.completions.create(
                        model="gpt-3.5-turbo",
                        messages=messages,
                    )
                    content_esg = response.choices[0].message.content
                    st.markdown(content_esg)
                except Exception as e:
                    st.error(f"Erro ao gerar informações ESG: {e}")
    elif aba == " Produtos ESG":
        st.title(" Produtos ESG")
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
                    st.markdown(f"[ Acessar Lâmina do Produto](./{p['arquivo']})")
                elif "lamina" in p:
                    st.markdown(f"[ Acessar Lâmina do Produto]({p['lamina']})")
    
                # Gráfico de rentabilidade acumulada e % retorno
                if p["nome"] in df_rent.columns:
                    df_plot = df_rent[["Data", p["nome"]]].copy()
                    
                    fig_rent = px.line(
                        df_plot,
                        x="Data",
                        y=[p["nome"]],
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
                        lambda t: t.update(line_color=ALTO_ESG) if t.name == p["nome"] else t.update(line_color="#888888", line_dash="dot")
                    )
                    st.plotly_chart(fig_rent, use_container_width=True)
                else:
                    st.info("Simulação de rentabilidade não disponível para este fundo.")

    elif aba == " Dashboard":
        st.title(" Análise ESG da Base de Clientes")

        # 👇 Garantir que a coluna ValorAlocadoESG exista (ou simular se estiver ausente)
        if "ValorAlocadoESG" not in df.columns:
            df["ValorAlocadoESG"] = np.random.uniform(50, 80, size=len(df)).round(2)
    
        # 👇 Garantir que a coluna ValorTotalCarteira exista
        if "ValorTotalCarteira" not in df.columns:
            # Supondo que o restante da carteira seja 2x o valor ESG (ajuste conforme necessário)
            df["ValorTotalCarteira"] = (df["ValorAlocadoESG"] * np.random.uniform(2.5, 5.0, size=len(df))).round(2)
    
    
            
        st.markdown("###  Indicador de Alocação ESG")

        # Verificação das colunas no DataFrame
        if "ValorAlocadoESG" in df.columns and "TicketMedioInvestido" in df.columns:

            capital_total = df["TicketMedioInvestido"].sum()
            capital_esg = df["ValorAlocadoESG"].sum()*1.81818181

            # Cálculo da proporção ESG (%)
            if capital_total > 0:
                percentual_esg = round((capital_esg / capital_total) * 100, 2)
            else:
                percentual_esg = 0.0

            # Meta futura (%)
            meta_percentual = 7  # você pode ajustar isso dinamicamente se quiser

            # Construção do gráfico tipo "velocímetro"
            fig_gauge = go.Figure(go.Indicator(
                mode="gauge+number+delta",
                value=percentual_esg,
                delta={'reference': meta_percentual, 'increasing': {'color': ALTO_ESG}, 'decreasing': {'color': "red"}},
                gauge={
                    'axis': {'range': [0, 100], 'tickwidth': 1, 'tickcolor': BAIXO_ESG},
                    'bar': {'color': ALTO_ESG, 'thickness': 0.3},
                    'bgcolor': BAIXO_ESG,
                    'steps': [
                        {'range': [0, percentual_esg], 'color': ALTO_ESG},
                        {'range': [percentual_esg, 100], 'color': BAIXO_ESG}
                    ],
                    'threshold': {
                        'line': {'color': COR_XP, 'width': 10},
                        'thickness': 1,
                        'value': meta_percentual
                    }
                },
                title={'text': "Proporção de Capital Alocado em ESG (%)"}
            ))

            fig_gauge.update_layout(
                height=400,
                font=dict(size=16),
                font_color="white"
            )

            st.plotly_chart(fig_gauge, use_container_width=True)

        else:
            st.warning("Colunas 'ValorAlocadoESG' e/ou 'ValorTotalCarteira' não encontradas na base.")
    
            
        _, col1, _ = st.columns(3)
        with col1:
            fig1 = px.pie(
                df,
                names="faixa_propensao",
                title="Distribuição por Faixa ESG",
                color="faixa_propensao",
                color_discrete_map={
                    "Alta": ALTO_ESG,
                    "Média": MEDIO_ESG,
                    "Baixa": BAIXO_ESG
                }
            )
            fig1.update_traces(textinfo="label+percent")
            st.plotly_chart(fig1, use_container_width=True)

        col3, col4, col5 = st.columns(3)
        with col3:
            st.markdown("###  Top 5 - Baixa Propensão")
            st.dataframe(top_baixa[["nome", "propensao_esg", "PerfilRisco"]])
        with col4:
            st.markdown("###  Top 5 - Média Propensão")
            st.dataframe(top_media[["nome", "propensao_esg", "PerfilRisco"]])
        with col5:
            st.markdown("###  Top 5 - Alta Propensão")
            st.dataframe(top_alta[["nome", "propensao_esg", "PerfilRisco"]])
       
    
        # NOVOS GRÁFICOS E INSIGHTS ESG
    
        st.markdown("###  Clientes com ativos vencendo em até 30 dias")

        if "vence_em_dias" in df.columns:
            vencendo_30 = df[df["vence_em_dias"] <= 30]
    
            # Agrupar corretamente
            agrupado = vencendo_30.groupby(["PerfilRisco", "faixa_propensao"]).size().reset_index(name="Quantidade")
    
            fig_vencendo = px.bar(
                agrupado,
                x="PerfilRisco",
                y="Quantidade",
                color="faixa_propensao",
                barmode="group",  # ← garante colunas agrupadas
                title="Clientes com Ativos Próximos do Vencimento",
                color_discrete_map={
                    "Alta": ALTO_ESG,
                    "Média": MEDIO_ESG,
                    "Baixa": BAIXO_ESG
                },
                labels={"PerfilRisco": "Perfil de Risco", "Quantidade": "Clientes"}
            )
    
            fig_vencendo.update_layout(
                height=450,
                bargap=0.2,
                font_color="#FFFFFF",
                legend_title_text="Faixa ESG"
            )
    
            st.plotly_chart(fig_vencendo, use_container_width=True)
        else:
            st.warning("Coluna 'vence_em_dias' não encontrada na base.")

    
        st.markdown("###  Distribuição de Clientes por Categoria de Produto e Faixa ESG")
    
        if "categoria_produto" in df.columns and "faixa_propensao" in df.columns:
            agrupado = df.groupby(["categoria_produto", "faixa_propensao"]).size().reset_index(name="Quantidade")
    
            fig_categoria = px.bar(
                agrupado,
                x="categoria_produto",
                y="Quantidade",
                color="faixa_propensao",
                barmode="group",
                title="Clientes por Categoria de Produto e Faixa ESG",
                color_discrete_map={
                    "Alta": ALTO_ESG,
                    "Média": MEDIO_ESG,
                    "Baixa": BAIXO_ESG
                },
                labels={"categoria_produto": "Categoria de Produto", "Quantidade": "Clientes"}
            )
    
            fig_categoria.update_layout(
                height=450,
                bargap=0.25,
                font_color="#FFFFFF",
                legend_title_text="Faixa ESG"
            )
    
            st.plotly_chart(fig_categoria, use_container_width=True)
        else:
            st.warning("Colunas necessárias não encontradas: 'categoria_produto' ou 'faixa_propensao'.")
        
        st.markdown("###  Maiores Oportunidades")

        if all(col in df.columns for col in ["propensao_esg", "ValorEmCaixa", "nome"]):
            # Calcular score baseado em capital * propensão
            df_temp = df.copy()
            df_temp["score"] = df_temp["ValorEmCaixa"] * df_temp["propensao_esg"]
            top_oportunidades = df_temp.sort_values(by="score", ascending=False).head(15)
    
            fig_top = px.scatter(
                top_oportunidades,
                x="propensao_esg",
                y="ValorEmCaixa",
                hover_name="nome",
                labels={
                    "propensao_esg": "Propensão ESG",
                    "ValorEmCaixa": "Capital Disponível (R$)"
                },
                title="Top 15 Clientes com Maior Capital e Propensão ESG"
            )
    
            fig_top.update_traces(
                marker=dict(color= ALTO_ESG, size=12, line=dict(width=1, color='black')),
                hovertemplate="<b>%{hovertext}</b><br>Propensão: %{x:.2f}<br>Capital: R$ %{y:,.2f}<extra></extra>"
            )
    
            fig_top.update_layout(height=500)
            st.plotly_chart(fig_top, use_container_width=True)
        else:
            st.warning("Colunas necessárias não encontradas: 'propensao_esg', 'ValorEmCaixa' ou 'nome'.")
    
        
        # ——— Antes do bloco da aba, garanta que os nomes estão limpos ———
    
    # ——— Sessão “Alocação Inteligente” ———
    elif aba == " Alocação Inteligente":
        st.title("Alocação Inteligente com ESG")
    
        # Seleção de cliente da base
        cliente_selecionado = st.selectbox("Selecione um cliente:", df["nome"].unique())
        cliente_info = df[df["nome"] == cliente_selecionado].iloc[0]
    
        # Pega o ticket médio investido desse cliente
        ticket_medio = cliente_info["TicketMedioInvestido"]
    
        # Normaliza o perfil para texto padronizado
        perfil_raw = cliente_info["PerfilRisco"]
        perfil = str(perfil_raw).strip().title()
        st.markdown(f"## Perfil de Investidor XP: **{perfil}**")
        st.markdown(f"### Ticket Médio Investido: R$ {ticket_medio:,.2f}")
    
        # Definições de alocação (% do ticket) por perfil
        mapping_perfis_pct = {
            "Conservador": {
                "Renda Fixa":    0.50,
                "Multimercado":  0.30,
                "Caixa":         0.20
            },
            "Moderado": {
                "Multimercado":  0.40,
                "Renda Fixa":    0.30,
                "ETF":           0.30
            },
            "Agressivo": {
                "Renda Variável":0.40,
                "ETF":           0.35,
                "Multimercado":  0.25
            }
        }
    
        # Constrói a carteira base em valores absolutos
        pct_carteira = mapping_perfis_pct.get(perfil, mapping_perfis_pct["Moderado"])
        carteira_base = {
            categoria: ticket_medio * pct
            for categoria, pct in pct_carteira.items()
        }
    
        # Produtos ESG disponíveis
        produtos_esg = [
            {"nome": "Fundo XP Essencial ESG", "categoria": "Renda Fixa",     "risco": 3},
            {"nome": "Pandhora ESG Prev",        "categoria": "Multimercado",  "risco": 7},
            {"nome": "ETF XP Sustentável",       "categoria": "ETF",           "risco": 10},
            {"nome": "Fundo XP Verde Ações",     "categoria": "Renda Variável","risco": 15}
        ]
    
        # Simular substituições parciais
        carteira_recomendada = []
        substituicoes = []
    
        for categoria, valor in carteira_base.items():
            # Mantém 'Caixa' sem ESG
            if categoria.lower() == "caixa":
                carteira_recomendada.append({"Produto": categoria, "Valor": valor})
                continue
    
            # Procura um produto ESG na mesma categoria
            esg_produto = next(
                (p for p in produtos_esg if p["categoria"].lower() == categoria.lower()),
                None
            )
            if esg_produto:
                valor_esg  = valor * 0.5
                valor_trad = valor * 0.5
                carteira_recomendada.extend([
                    {"Produto": f"{categoria} Tradicional", "Valor": valor_trad},
                    {"Produto": esg_produto["nome"],       "Valor": valor_esg}
                ])
                substituicoes.append({
                    "Categoria":       categoria,
                    "ESG Sugerido":    esg_produto["nome"],
                    "Porcentagem ESG": "50%",
                    "Motivo":          "Risco compatível e disponível ESG na mesma classe"
                })
            else:
                carteira_recomendada.append({"Produto": categoria, "Valor": valor})
    
        # Exibição dos gráficos
        col1, col2 = st.columns(2)
    
        with col1:
            df_atual = pd.DataFrame({
                "Produto": list(carteira_base.keys()),
                "Valor":   list(carteira_base.values())
            })
            fig1 = px.pie(
                df_atual,
                names="Produto",
                values="Valor",
                title="Carteira Atual por Categoria",
                color="Produto",
                color_discrete_map={
                    "Renda Variável": TRAD1,
                    "ETF": TRAD2,
                    "Multimercado": TRAD3}
            )
            st.plotly_chart(fig1, use_container_width=True)
    
        with col2:
            df_nova = pd.DataFrame(carteira_recomendada)
            fig2 = px.pie(
                df_nova,
                names="Produto",
                values="Valor",
                title="Carteira Recomendada com ESG",
                 color="Produto",
                color_discrete_map={
                    "Renda Variável Tradicional": TRAD1,
                    "ETF Tradicional": TRAD2,
                    "Multimercado Tradicional": TRAD3,
                    "Fundo XP Verde Ações": ALTO_ESG,
                    "ETF XP Sustentável": MEDIO_ESG,
                    "Pandhora ESG Prev": PROD_ESG
                }
            )
            st.plotly_chart(fig2, use_container_width=True)
    
        # Tabela de substituições
        if substituicoes:
            st.markdown("### Substituições Recomendadas")
            st.dataframe(pd.DataFrame(substituicoes))
        else:
            st.info("Nenhuma substituição ESG recomendada no momento.")
                
    elif aba == " Campanha":
        st.title(" Campanha de Alocação ESG")
    
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
        st.markdown("###  Alocação Acumulada ao Longo do Tempo")
        fig_crescimento = px.line(
            df_campanha,
            x="Data",
            y="Assessor",
            title="Alocação ESG - Assessor",
            markers=True,
            labels={"Assessor": "Valor Acumulado (R$)"},
            line_shape="linear"
        )
        fig_crescimento.update_traces(line=dict(color=ALTO_ESG, width=3))
    
        st.plotly_chart(fig_crescimento, use_container_width=True)
    
        # Gráfico comparativo: assessor vs XP
        st.markdown("###  Comparativo com Média da XP")
        total_assessor = aloc_assessor[-1]
        total_xp = aloc_xp[-1]
    
        fig_barra = px.bar(
            x=["Assessor", "Média XP"],
            y=[total_assessor, total_xp],
            labels={"x": "Origem", "y": "Valor Total Alocado"},
            color_discrete_map={
                    "Assessor": ALTO_ESG,
                    "Média XP": MEDIO_ESG
                    },
            title="Total Alocado no Ano"
        )
        st.plotly_chart(fig_barra, use_container_width=True)
    
        # Estatísticas gerais
        st.markdown("### 🧾 Estatísticas da Campanha")
        st.metric("Total Alocado pelo Assessor", f"R$ {total_assessor:,.0f}")
        st.metric("Média de Alocação XP", f"R$ {total_xp:,.0f}")
