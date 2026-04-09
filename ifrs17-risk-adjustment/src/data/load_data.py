"""
Data Loading Module

Carrega dados de fonte externa (Kaggle) ou arquivo local.
Simula dados de seguros/previdência com variáveis críticas para IFRS 17.

Variáveis principais:
- claim: indicador de sinistro (0/1)
- claim_amount: valor do sinistro (quando aplicável)
- age: idade do segurado
- premium: prêmio pago
- region: região geográfica
- duration: duração do contrato
- lapses: taxa de cancelamento
"""

import pandas as pd
import numpy as np
from pathlib import Path


def load_from_kaggle(filepath: str = None) -> pd.DataFrame:
    """
    Carrega dataset de seguro do Kaggle.

    Args:
        filepath: caminho para arquivo CSV

    Returns:
        DataFrame com dados de sinistros
    """
    if filepath and Path(filepath).exists():
        return pd.read_csv(filepath)
    else:
        return generate_synthetic_data()


def generate_synthetic_data(n_records: int = 5000) -> pd.DataFrame:
    """
    Gera dados sintéticos realistas para teste do modelo.

    Simula portfólio de seguros com estrutura atuarial.

    Args:
        n_records: número de registros a gerar

    Returns:
        DataFrame com dados sintéticos
    """
    np.random.seed(42)

    data = pd.DataFrame({
        'claim_id': np.arange(n_records),
        'age': np.random.randint(18, 85, n_records),
        'region': np.random.choice(['North', 'South', 'East', 'West'], n_records),
        'premium': np.random.lognormal(mean=8, sigma=1, size=n_records),
        'duration': np.random.randint(1, 30, n_records),
        'claim': np.random.binomial(1, 0.15, n_records),
        'claim_amount': np.random.lognormal(mean=9, sigma=1.5, size=n_records),
        'lapse': np.random.binomial(1, 0.08, n_records),
    })

    # Adiciona fatores de risco correlacionados
    data['risk_score'] = (
        (data['age'] / 100) * 0.3 +
        (data['duration'] / 30) * 0.3 +
        np.random.uniform(0, 1, n_records) * 0.4
    )

    return data


def load_data(source: str = 'synthetic', filepath: str = None) -> pd.DataFrame:
    """
    Função principal de carregamento de dados.

    Args:
        source: tipo de fonte ('synthetic' ou 'csv')
        filepath: caminho do arquivo (se source='csv')

    Returns:
        DataFrame processado
    """
    if source == 'csv':
        data = load_from_kaggle(filepath)
    else:
        data = generate_synthetic_data()

    print(f"Dados carregados: {len(data)} registros, {len(data.columns)} colunas")
    return data
