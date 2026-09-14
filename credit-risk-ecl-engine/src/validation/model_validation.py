"""
Validação estatística do modelo de PD.

Métricas padrão de mercado para modelos de credit scoring:
- Gini / AUC: poder discriminante (capacidade de separar bons e maus pagadores).
- KS (Kolmogorov-Smirnov): distância máxima entre as distribuições
  cumulativas de bons e maus pagadores.
- PSI (Population Stability Index): estabilidade da distribuição de PD
  entre duas amostras (ex.: treino vs. teste, ou safra vs. safra) — usado
  para monitoramento contínuo do modelo em produção.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def gini_from_auc(auc: float) -> float:
    return 2 * auc - 1


def psi(expected: np.ndarray, actual: np.ndarray, n_bins: int = 10) -> float:
    """Population Stability Index entre duas distribuições de score/PD.

    Regra de mercado: PSI < 0.10 = estável; 0.10-0.25 = atenção;
    > 0.25 = mudança significativa (recalibração recomendada).
    """
    breakpoints = np.quantile(expected, np.linspace(0, 1, n_bins + 1))
    breakpoints[0] = -np.inf
    breakpoints[-1] = np.inf

    expected_pct = np.histogram(expected, bins=breakpoints)[0] / len(expected)
    actual_pct = np.histogram(actual, bins=breakpoints)[0] / len(actual)

    expected_pct = np.clip(expected_pct, 1e-4, None)
    actual_pct = np.clip(actual_pct, 1e-4, None)

    return float(np.sum((actual_pct - expected_pct) * np.log(actual_pct / expected_pct)))


def psi_rating(psi_value: float) -> str:
    if psi_value < 0.10:
        return "estável"
    if psi_value < 0.25:
        return "atenção"
    return "mudança significativa"


def calibration_table(pd_pred: np.ndarray, y_true: np.ndarray, n_bins: int = 10) -> pd.DataFrame:
    """Compara PD prevista vs. taxa de default observada por decil de
    score — teste de calibração (fundamental para justificar o uso da PD
    em ECL perante auditoria/regulador)."""
    df = pd.DataFrame({"pd_pred": pd_pred, "y_true": y_true})
    df["decile"] = pd.qcut(df["pd_pred"], n_bins, labels=False, duplicates="drop")

    table = (
        df.groupby("decile")
        .agg(n=("y_true", "count"), pd_media_prevista=("pd_pred", "mean"), taxa_default_observada=("y_true", "mean"))
        .reset_index()
    )
    table["desvio_absoluto"] = (table["pd_media_prevista"] - table["taxa_default_observada"]).abs()
    return table
