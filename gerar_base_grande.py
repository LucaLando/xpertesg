import numpy as np
import pandas as pd

def gerar_base_clientes_grande(n=4400000):
    np.random.seed(42)

    df3 = pd.DataFrame({
        'Idade': np.random.randint(18, 70, n),
        'Renda': np.random.normal(12000, 4000, n).clip(2000, 30000),
        'TempoDeRelacao': np.random.randint(1, 121, n),
        'TicketMedioInvestido': np.random.uniform(10000, 2_000_000, n),
        'QtdProdutosNaCarteira': np.random.randint(1, 20, n),
        'PerfilRisco': np.random.choice([0, 1, 2], n, p=[0.3, 0.5, 0.2]),
        'Pais': np.random.choice(['Brasil', 'EUA', 'Alemanha'], n, p=[0.7, 0.2, 0.1]),
        'TaxaJuros': np.random.choice([13.75, 5.0, 2.0], n, p=[0.7, 0.2, 0.1])
    })

    df3['HistoricoInvestimentoESG'] = np.random.binomial(1, 0.3, n)

    df3['EngajamentoESG'] = np.where(df3['HistoricoInvestimentoESG'] == 1,
                                     np.random.randint(8, 15, n),
                                     np.random.randint(0, 8, n))
    df3['ConhecimentoESG'] = np.where(df3['HistoricoInvestimentoESG'] == 1,
                                      np.random.randint(3, 6, n),
                                      np.random.randint(1, 4, n))
    df3['PreocupacaoAmbiental'] = np.clip(df3['ConhecimentoESG'] + np.random.randint(-1, 2, n), 1, 5)

    df3['AcessouPagESG'] = np.where(df3['HistoricoInvestimentoESG'] == 1,
                                    np.random.binomial(1, 0.7, n),
                                    np.random.binomial(1, 0.3, n))
    df3['LeuArtigoESG'] = np.where(df3['HistoricoInvestimentoESG'] == 1,
                                   np.random.binomial(1, 0.6, n),
                                   np.random.binomial(1, 0.2, n))
    df3['ParticipouWebinarESG'] = np.where(df3['HistoricoInvestimentoESG'] == 1,
                                           np.random.binomial(1, 0.4, n),
                                           np.random.binomial(1, 0.1, n))
    df3['AssessorESGAtivo'] = np.where(df3['HistoricoInvestimentoESG'] == 1,
                                       np.random.binomial(1, 0.6, n),
                                       np.random.binomial(1, 0.2, n))

    df3['NPS_ESG'] = np.clip((df3['EngajamentoESG'] / 1.5).astype(int) + np.random.randint(-1, 2, n), 0, 10)

    df3['ValorAlocadoESG'] = df3['HistoricoInvestimentoESG'] * np.random.uniform(5000, 100000, n)

    proba_esg = (
        0.25 * df3['HistoricoInvestimentoESG'] +
        0.2 * df3['ParticipouWebinarESG'] +
        0.15 * df3['LeuArtigoESG'] +
        0.1 * df3['AcessouPagESG'] +
        0.1 * (df3['NPS_ESG'] >= 8).astype(int) +
        0.1 * (df3['EngajamentoESG'] >= 10).astype(int) +
        0.1 * (df3['ConhecimentoESG'] >= 4).astype(int) +
        0.2 * df3['AssessorESGAtivo']
    )

    df3['ESG_Label'] = np.random.binomial(1, np.clip(proba_esg, 0, 1))
    return df3
