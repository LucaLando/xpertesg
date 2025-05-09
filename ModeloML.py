
import pandas as pd
import numpy as np

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
