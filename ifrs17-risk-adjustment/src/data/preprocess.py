"""
Preprocessamento de Dados

Limpeza, transformação e normalização de dados brutos.
Garante qualidade e consistência para modelagem.
"""

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler


def handle_missing_values(data: pd.DataFrame, strategy: str = 'drop') -> pd.DataFrame:
    """
    Trata valores ausentes.

    Args:
        data: DataFrame com dados brutos
        strategy: 'drop' ou 'mean'

    Returns:
        DataFrame sem valores ausentes
    """
    if strategy == 'drop':
        data = data.dropna()
    elif strategy == 'mean':
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        data[numeric_cols] = data[numeric_cols].fillna(data[numeric_cols].mean())

    return data


def encode_categorical(data: pd.DataFrame) -> pd.DataFrame:
    """
    Codifica variáveis categóricas usando factorize.

    Args:
        data: DataFrame com colunas categóricas

    Returns:
        DataFrame com variáveis codificadas
    """
    cat_cols = data.select_dtypes(include=['object']).columns

    for col in cat_cols:
        # Usa factorize para converter strings em números
        data[col] = pd.factorize(data[col])[0]

    return data


def normalize_numeric(data: pd.DataFrame, exclude: list = None) -> tuple:
    """
    Normaliza variáveis numéricas usando StandardScaler.

    Args:
        data: DataFrame
        exclude: colunas a excluir da normalização

    Returns:
        DataFrame normalizado e scaler
    """
    if exclude is None:
        exclude = ['claim_status', 'claim_id', 'policy_id']

    numeric_cols = data.select_dtypes(include=[np.number]).columns
    cols_to_scale = [col for col in numeric_cols if col not in exclude]

    if len(cols_to_scale) == 0:
        return data, None

    scaler = StandardScaler()
    data[cols_to_scale] = scaler.fit_transform(data[cols_to_scale])

    return data, scaler


def add_interaction_features(data: pd.DataFrame) -> pd.DataFrame:
    """
    Cria variáveis de interação relevantes.

    Detecta automaticamente colunas disponíveis e cria interações.

    Args:
        data: DataFrame processado

    Returns:
        DataFrame com variáveis adicionais
    """
    # Detecta se existem colunas numéricas relevantes para interação
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()

    # Se houver pelo menos 2 colunas numéricas, cria algumas interações
    if len(numeric_cols) >= 2:
        # Pega as duas primeiras colunas numéricas (excluindo target)
        col1 = numeric_cols[0]
        col2 = numeric_cols[1] if numeric_cols[1] != 'claim_status' else (numeric_cols[2] if len(numeric_cols) > 2 else numeric_cols[0])

        # Cria interação normalizada
        data[f'{col1}_x_{col2}'] = (data[col1] * data[col2]) / (np.abs(data[col1] * data[col2]).max() + 1e-8)

    return data


def preprocess(data: pd.DataFrame, normalize: bool = True):
    """
    Pipeline completo de preprocessamento.

    Args:
        data: DataFrame bruto
        normalize: se deve normalizar variáveis

    Returns:
        DataFrame pronto para modelagem e scaler (se normalize=True)
    """
    # Faz cópia para não modificar original
    data = data.copy()

    # Etapa 1: Trata valores ausentes
    data = handle_missing_values(data, strategy='mean')
    print("[1/4] Valores ausentes tratados")

    # Etapa 2: Codifica categóricas
    data = encode_categorical(data)
    print("[2/4] Variáveis categóricas codificadas")

    # Etapa 3: Cria features de interação
    data = add_interaction_features(data)
    print("[3/4] Variáveis de interação criadas")

    # Etapa 4: Normaliza (opcional)
    scaler = None
    if normalize:
        data, scaler = normalize_numeric(data)
        print("[4/4] Variáveis normalizadas")
        return data, scaler

    print("[4/4] Normalização pulada")
    return data, None
