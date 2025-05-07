
st.set_page_config(page_title="XPertESG", layout="wide")

# Inserir logo XP Inc. na barra lateral
st.sidebar.image("https://seeklogo.com/images/X/xp-inc-logo-083C1A92A7-seeklogo.com.png", width=180)

# CSS customizado XP Inc.
st.markdown(
    '''
    <style>
    /* Fonte padrão XP Inc */
    @import url('https://fonts.googleapis.com/css2?family=Open+Sans:wght@300;400;700&display=swap');

    html, body, [class*="css"]  {
        font-family: 'Open Sans', sans-serif;
        background-color: #000000;
        color: #ffffff;
    }

    /* Sidebar fundo e padding */
    section[data-testid="stSidebar"] {
        background-color: #000000;
        padding: 1rem;
        border-right: 2px solid #FECB00;
    }

    /* Títulos */
    h1, h2, h3 {
        color: #FECB00;
        font-weight: 700;
    }

    /* Expanders e caixas */
    .streamlit-expanderHeader {
        font-weight: bold;
        color: #FECB00;
    }

    /* Botões amarelos com texto preto */
    button[kind="primary"] {
        background-color: #FECB00 !important;
        color: black !important;
        border-radius: 8px;
        font-weight: bold;
    }

    /* Inputs */
    .stTextInput, .stSelectbox, .stNumberInput, .stTextArea {
        background-color: #111;
        color: white;
        border: 1px solid #FECB00;
    }

    /* Tabelas */
    .stDataFrame {
        background-color: #000;
        color: white;
    }

    /* Rodapé invisível */
    footer {
        visibility: hidden;
    }
    </style>
    ''',
    unsafe_allow_html=True
)
