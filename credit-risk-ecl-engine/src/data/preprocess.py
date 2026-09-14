"""
Pré-processamento e engenharia de atributos da carteira de crédito.

Responsabilidades:
- Segmentação de portfólio (necessária para a modelagem de correlação via
  cópulas no módulo de simulação — Seção 4 do relatório de metodologia).
- Codificação ordinal de variáveis de risco (status da conta, poupança,
  tempo de emprego) preservando a ordem de risco crescente/decrescente.
- One-hot encoding das variáveis nominais restantes.
- Split treino/teste estratificado pelo target.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.model_selection import train_test_split

TARGET_COLUMN = "default"

# Mapas ordinais — do maior para o menor risco de crédito (quanto maior o
# valor, maior a garantia/estabilidade do tomador e, portanto, menor o risco).
_STATUS_ORDER = {
    "no checking account": 3,
    "... >= 200 DM / salary assignments for at least 1 year": 2,
    "0 <= ... < 200 DM": 1,
    "... < 0 DM": 0,
}
_SAVINGS_ORDER = {
    "... >= 1000 DM": 4,
    "500 <= ... < 1000 DM": 3,
    "100 <= ... < 500 DM": 2,
    "... < 100 DM": 1,
    "unknown/no savings account": 0,
}
_EMPLOYMENT_ORDER = {
    "... >= 7 years": 4,
    "4 <= ... < 7 years": 3,
    "1 <= ... < 4 years": 2,
    "... < 1 year": 1,
    "unemployed": 0,
}

NOMINAL_COLUMNS = [
    "credit_history",
    "purpose",
    "personal_status_sex",
    "other_debtors",
    "property",
    "other_installment_plans",
    "housing",
    "job",
    "telephone",
    "foreign_worker",
]


def assign_segment(df: pd.DataFrame) -> pd.Series:
    """Segmenta a carteira em linhas de negócio para fins de correlação
    de risco (usado no motor de simulação por cópulas).

    Segmentação simplificada por finalidade do crédito, agrupada em 4
    macro-segmentos análogos a linhas de produto bancário.
    """
    mapping = {
        "car (new)": "veiculos",
        "car (used)": "veiculos",
        "domestic appliances": "bens_consumo",
        "furniture/equipment": "bens_consumo",
        "radio/television": "bens_consumo",
        "repairs": "bens_consumo",
        "business": "pj_capital_giro",
        "education": "pessoal",
        "retraining": "pessoal",
        "vacation": "pessoal",
        "others": "pessoal",
    }
    return df["purpose"].map(mapping).fillna("pessoal")


def encode_features(df: pd.DataFrame) -> pd.DataFrame:
    """Codifica variáveis categóricas mantendo `contract_id`, `segment`
    e o target intactos.
    """
    out = df.copy()
    out["status_ord"] = out["status"].map(_STATUS_ORDER).fillna(1)
    out["savings_ord"] = out["savings"].map(_SAVINGS_ORDER).fillna(0)
    out["employment_ord"] = out["employment_duration"].map(_EMPLOYMENT_ORDER).fillna(0)
    out = out.drop(columns=["status", "savings", "employment_duration"])

    out["segment"] = assign_segment(out)

    # Preserva a coluna original de colateral (não-codificada) para uso
    # posterior no modelo de LGD, que precisa do rótulo textual da
    # garantia — o one-hot encoding abaixo gera colunas com outro nome
    # (`property_...`) e não colide com esta cópia.
    raw_for_downstream = out[["property"]].copy()

    dummies = pd.get_dummies(out[NOMINAL_COLUMNS], prefix=NOMINAL_COLUMNS, drop_first=True)
    out = pd.concat([out.drop(columns=NOMINAL_COLUMNS), dummies, raw_for_downstream], axis=1)
    return out


@dataclass
class PreparedData:
    df_full: pd.DataFrame           # dataset codificado completo (para ECL/relatórios)
    X_train: pd.DataFrame
    X_test: pd.DataFrame
    y_train: pd.Series
    y_test: pd.Series
    feature_columns: list[str]


def prepare_dataset(df: pd.DataFrame, test_size: float = 0.25, random_state: int = 42) -> PreparedData:
    encoded = encode_features(df)

    non_feature_cols = {"contract_id", "segment", "property", TARGET_COLUMN}
    feature_columns = [c for c in encoded.columns if c not in non_feature_cols]

    X = encoded[feature_columns]
    y = encoded[TARGET_COLUMN]

    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=test_size, random_state=random_state, stratify=y
    )

    return PreparedData(
        df_full=encoded,
        X_train=X_train,
        X_test=X_test,
        y_train=y_train,
        y_test=y_test,
        feature_columns=feature_columns,
    )
