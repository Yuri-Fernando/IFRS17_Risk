"""
Modelagem de PD (Probability of Default).

Dois modelos são treinados e comparados (Artigo VI do gate de qualidade —
comparação de modelos é exigida para justificar a escolha em auditoria):

1. Regressão Logística — modelo de referência ("champion" regulatório),
   interpretável, exigido tipicamente para explicabilidade em modelos de
   crédito (SR 11-7 / Resolução CMN 4.966 — governança de modelos).
2. Gradient Boosting — modelo "challenger", não-linear, usado para
   avaliar ganho de poder discriminante (Gini/KS) frente ao champion.

Ambos calculam PD 12 meses (usada no Stage 1) e Gini/KS/AUC de avaliação.
A extrapolação para PD lifetime (Stage 2/3) é feita em `staging.py`.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from sklearn.ensemble import GradientBoostingClassifier
from sklearn.linear_model import LogisticRegression
from sklearn.metrics import roc_auc_score, roc_curve
from sklearn.preprocessing import StandardScaler


@dataclass
class PDModelResult:
    model_name: str
    model: object
    scaler: StandardScaler | None
    auc: float
    gini: float
    ks: float
    pd_train: np.ndarray
    pd_test: np.ndarray


def _ks_statistic(y_true: np.ndarray, y_score: np.ndarray) -> float:
    fpr, tpr, _ = roc_curve(y_true, y_score)
    return float(np.max(np.abs(tpr - fpr)))


def train_logistic_pd(X_train, y_train, X_test, y_test) -> PDModelResult:
    scaler = StandardScaler()
    X_train_s = scaler.fit_transform(X_train)
    X_test_s = scaler.transform(X_test)

    model = LogisticRegression(max_iter=2000, class_weight="balanced", C=1.0)
    model.fit(X_train_s, y_train)

    pd_train = model.predict_proba(X_train_s)[:, 1]
    pd_test = model.predict_proba(X_test_s)[:, 1]

    auc = roc_auc_score(y_test, pd_test)
    return PDModelResult(
        model_name="logistic_regression",
        model=model,
        scaler=scaler,
        auc=auc,
        gini=2 * auc - 1,
        ks=_ks_statistic(y_test, pd_test),
        pd_train=pd_train,
        pd_test=pd_test,
    )


def train_gbm_pd(X_train, y_train, X_test, y_test, random_state: int = 42) -> PDModelResult:
    model = GradientBoostingClassifier(
        n_estimators=200,
        max_depth=3,
        learning_rate=0.05,
        subsample=0.8,
        random_state=random_state,
    )
    model.fit(X_train, y_train)

    pd_train = model.predict_proba(X_train)[:, 1]
    pd_test = model.predict_proba(X_test)[:, 1]

    auc = roc_auc_score(y_test, pd_test)
    return PDModelResult(
        model_name="gradient_boosting",
        model=model,
        scaler=None,
        auc=auc,
        gini=2 * auc - 1,
        ks=_ks_statistic(y_test, pd_test),
        pd_train=pd_train,
        pd_test=pd_test,
    )


def score_full_portfolio(result: PDModelResult, X_full: pd.DataFrame) -> np.ndarray:
    """Aplica o modelo treinado (champion) na carteira completa para gerar
    a PD 12 meses de cada contrato — insumo do módulo de ECL."""
    if result.scaler is not None:
        X_scored = result.scaler.transform(X_full)
    else:
        X_scored = X_full
    return result.model.predict_proba(X_scored)[:, 1]


def select_champion(candidates: list[PDModelResult]) -> PDModelResult:
    """Seleciona o modelo com maior Gini no conjunto de teste.

    Critério documentado em `reports/model_comparison.md`.
    """
    return max(candidates, key=lambda r: r.gini)
