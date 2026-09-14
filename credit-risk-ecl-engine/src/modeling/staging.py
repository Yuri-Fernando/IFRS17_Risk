"""
Classificação de Stage IFRS 9 (§ 5.5 / Resolução CMN 4.966) e extrapolação
de PD 12 meses para PD lifetime.

Regras de staging (SICR — Significant Increase in Credit Risk):
- Stage 1: risco de crédito não aumentou significativamente desde a
  originação → ECL reconhecida em base de 12 meses.
- Stage 2: aumento significativo de risco desde a originação, mas sem
  evidência objetiva de perda (não inadimplente) → ECL lifetime.
- Stage 3: evidência objetiva de perda / inadimplência (credit-impaired)
  → ECL lifetime, com PD = 100% (evento já materializado).

Como o dataset não traz PD de originação histórica, ela é aproximada por
um "PD de originação" simulada a partir do score de crédito no momento da
concessão (proxy: mesma PD do modelo, ajustada por um fator de add-on
temporal). Essa premissa está documentada em `reports/assumptions.md`.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

STAGE_1, STAGE_2, STAGE_3 = 1, 2, 3


def estimate_origination_pd(pd_current: np.ndarray, seed: int = 7) -> np.ndarray:
    """Proxy de PD na data de originação.

    Como não há PD histórica real disponível no dataset, aplicamos um
    fator multiplicativo aleatório (ruído log-normal com média 1) para
    simular a evolução natural do risco entre a concessão e a data-base —
    premissa conservadora documentada e sujeita a validação com dados
    reais de safra (vintage analysis) em produção.
    """
    rng = np.random.default_rng(seed)
    drift = rng.lognormal(mean=0.0, sigma=0.25, size=len(pd_current))
    origination_pd = np.clip(pd_current / drift, 1e-4, 0.99)
    return origination_pd


def classify_stage(
    pd_current: np.ndarray,
    pd_origination: np.ndarray,
    is_default: np.ndarray,
    sicr_threshold_ratio: float = 2.0,
    sicr_absolute_threshold: float = 0.20,
) -> np.ndarray:
    """Aplica critérios de SICR.

    Um contrato migra para Stage 2 se:
    - PD atual >= `sicr_threshold_ratio` x PD de originação (deterioração
      relativa), OU
    - PD atual >= `sicr_absolute_threshold` (piso absoluto de risco alto).

    Contratos com `is_default == 1` são sempre Stage 3.
    """
    relative_deterioration = pd_current >= (sicr_threshold_ratio * pd_origination)
    absolute_high_risk = pd_current >= sicr_absolute_threshold

    stage = np.where(relative_deterioration | absolute_high_risk, STAGE_2, STAGE_1)
    stage = np.where(is_default == 1, STAGE_3, stage)
    return stage.astype(int)


def lifetime_pd(pd_12m: np.ndarray, term_months: np.ndarray) -> np.ndarray:
    """Extrapola PD 12 meses para PD lifetime assumindo uma hazard rate
    constante (aproximação de sobrevivência exponencial):

        PD_lifetime = 1 - (1 - PD_12m) ** (term_months / 12)

    Aproximação padrão de mercado para portfólios sem curva de PD marginal
    completa por safra; documentada como simplificação em
    `reports/assumptions.md`.
    """
    years = np.maximum(term_months / 12.0, 1.0)
    survival_12m = 1 - pd_12m
    survival_12m = np.clip(survival_12m, 1e-6, 1.0)
    return 1 - survival_12m ** years


def apply_staging(df: pd.DataFrame, pd_12m: np.ndarray) -> pd.DataFrame:
    out = df.copy()
    out["pd_12m"] = pd_12m
    out["pd_origination"] = estimate_origination_pd(pd_12m)
    out["stage"] = classify_stage(
        pd_current=out["pd_12m"].values,
        pd_origination=out["pd_origination"].values,
        is_default=out["default"].values,
    )
    out["pd_lifetime"] = lifetime_pd(out["pd_12m"].values, out["term_months"].values)
    out["pd_lifetime"] = np.where(out["stage"] == STAGE_3, 1.0, out["pd_lifetime"])
    return out
