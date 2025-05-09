
import pandas as pd
import numpy as np
from sklearn.pipeline import Pipeline
from sklearn.ensemble import RandomForestClassifier
from sklearn.preprocessing import OneHotEncoder, StandardScaler
from sklearn.compose import ColumnTransformer

def simular_base_clientes(n=1000):
    np.random.seed(42)
    dados = {
        "nome": [f"Cliente {i+1}" for i in range(n)],
        "idade": np.random.randint(18, 75, size=n),
        "renda": np.random.normal(10000, 3000, size=n).round(2),
        "ticket_medio_investido": np.random.normal(40000, 15000, size=n).round(2),
        "perfil_risco": np.random.choice(["Conservador", "Moderado", "Agressivo"], size=n),
        "conhecimento_esg": np.random.randint(0, 6, size=n),
        "engajamento_esg": np.random.randint(0, 6, size=n)
    }
    return pd.DataFrame(dados)

def carregar_modelo_pipeline():
    # Simulação de treino direto no código (substitua por modelo real se necessário)
    df_sim = pd.DataFrame({
        "idade": np.random.randint(18, 75, size=100),
        "renda": np.random.normal(10000, 3000, size=100),
        "ticket_medio_investido": np.random.normal(40000, 15000, size=100),
        "perfil_risco": np.random.choice(["Conservador", "Moderado", "Agressivo"], size=100),
        "conhecimento_esg": np.random.randint(0, 6, size=100),
        "engajamento_esg": np.random.randint(0, 6, size=100),
        "esg": np.random.choice([0, 1], size=100)
    })

    features = ["idade", "renda", "ticket_medio_investido", "perfil_risco", "conhecimento_esg", "engajamento_esg"]
    target = "esg"

    cat_features = ["perfil_risco"]
    num_features = ["idade", "renda", "ticket_medio_investido", "conhecimento_esg", "engajamento_esg"]

    preprocessor = ColumnTransformer([
        ("num", StandardScaler(), num_features),
        ("cat", OneHotEncoder(), cat_features)
    ])

    pipe = Pipeline([
        ("preprocessor", preprocessor),
        ("classificador", RandomForestClassifier(n_estimators=100, random_state=42))
    ])

    pipe.fit(df_sim[features], df_sim[target])
    return pipe
