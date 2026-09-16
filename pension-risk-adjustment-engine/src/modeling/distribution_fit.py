"""
Seleção de distribuição estatística por critério combinado (AIC/BIC + KS),
conforme metodologia (itau/METODOLOGIA_MESTRE.md, seção 3.4): nunca escolher
uma distribuição só porque "o critério estatístico apontou" — o resultado
inclui também a razoabilidade teórica do suporte de cada candidata.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class FitResult:
    distribution: str
    params: tuple
    aic: float
    bic: float
    ks_statistic: float
    ks_pvalue: float


_DIST_MAP = {
    "gamma": stats.gamma,
    "lognorm": stats.lognorm,
    "norm": stats.norm,
}

_SUPPORT_NOTE = {
    "gamma": "suporte em [0, +inf) — compatível com sinistralidade/valores sempre não-negativos, cauda direita mais pesada que a normal",
    "lognorm": "suporte em (0, +inf) — assimetria positiva, mas cauda mais pesada que a gamma para o mesmo CV em muitos regimes",
    "norm": "suporte em (-inf, +inf) — permite valores negativos, teoricamente inadequado para uma sinistralidade que nunca é negativa",
}


def fit_distribution(data: np.ndarray, dist_name: str) -> FitResult:
    dist = _DIST_MAP[dist_name]
    data = np.asarray(data, dtype=float)
    data = data[data > 0] if dist_name == "lognorm" else data

    params = dist.fit(data)
    log_likelihood = np.sum(dist.logpdf(data, *params))
    k = len(params)
    n = len(data)
    aic = 2 * k - 2 * log_likelihood
    bic = k * np.log(n) - 2 * log_likelihood
    ks_stat, ks_p = stats.kstest(data, dist_name, args=params)

    return FitResult(distribution=dist_name, params=params, aic=aic, bic=bic, ks_statistic=ks_stat, ks_pvalue=ks_p)


def select_best_distribution(data: np.ndarray, candidates: list[str] | None = None) -> tuple[FitResult, pd.DataFrame]:
    """Ajusta todas as candidatas, retorna a de menor AIC como escolhida e uma
    tabela comparativa completa (para auditoria/transparência — requisito
    central identificado na metodologia, seção 2 Fase 5)."""
    candidates = candidates or list(_DIST_MAP.keys())
    results = [fit_distribution(data, name) for name in candidates]

    comparison = pd.DataFrame(
        [
            {
                "distribution": r.distribution,
                "aic": r.aic,
                "bic": r.bic,
                "ks_statistic": r.ks_statistic,
                "ks_pvalue": r.ks_pvalue,
                "support_note": _SUPPORT_NOTE[r.distribution],
            }
            for r in results
        ]
    ).sort_values("aic").reset_index(drop=True)

    best_name = comparison.iloc[0]["distribution"]
    best_result = next(r for r in results if r.distribution == best_name)
    return best_result, comparison
