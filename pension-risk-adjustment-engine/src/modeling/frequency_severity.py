"""
Decomposição Frequência x Severidade (visão complementar ao A/E e à
sinistralidade agregada) — conforme itau/METODOLOGIA_MESTRE.md seção 3.4:
frequência mensal de eventos (Poisson vs. Binomial Negativa, escolhendo a
Binomial Negativa quando há sobre-dispersão) e severidade individual por
evento (Lognormal).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import stats


@dataclass
class FrequencyFitResult:
    distribution: str
    mean: float
    variance: float
    dispersion_ratio: float  # variância / média — > 1 indica sobre-dispersão (favorece NB sobre Poisson)
    params: tuple
    aic: float


def fit_frequency(monthly_counts: np.ndarray) -> tuple[FrequencyFitResult, pd.DataFrame]:
    """Compara Poisson vs. Binomial Negativa na série de contagem mensal de
    eventos. Critério de decisão: sobre-dispersão (var/mean > 1) + AIC."""
    counts = np.asarray(monthly_counts, dtype=float)
    mean = counts.mean()
    var = counts.var(ddof=1)
    dispersion_ratio = var / mean if mean > 0 else np.nan

    # Poisson: log-likelihood fechado com lambda = média amostral
    lam = mean
    ll_poisson = np.sum(stats.poisson.logpmf(counts, lam))
    aic_poisson = 2 * 1 - 2 * ll_poisson

    # Binomial Negativa: parametrização via método dos momentos (r, p)
    # var = mean + mean^2 / r  =>  r = mean^2 / (var - mean), se var > mean
    if var > mean:
        r = mean**2 / (var - mean)
        p = r / (r + mean)
        ll_nbinom = np.sum(stats.nbinom.logpmf(counts, r, p))
        aic_nbinom = 2 * 2 - 2 * ll_nbinom
        nb_params = (r, p)
    else:
        # sem sobre-dispersão: NB degenera para Poisson, AIC pior por parâmetro extra
        r, p = np.inf, 1.0
        aic_nbinom = aic_poisson + 2
        nb_params = (r, p)

    comparison = pd.DataFrame(
        [
            {"distribution": "poisson", "aic": aic_poisson, "params": (lam,)},
            {"distribution": "nbinom", "aic": aic_nbinom, "params": nb_params},
        ]
    ).sort_values("aic").reset_index(drop=True)

    best = comparison.iloc[0]
    result = FrequencyFitResult(
        distribution=best["distribution"],
        mean=mean,
        variance=var,
        dispersion_ratio=dispersion_ratio,
        params=tuple(best["params"]),
        aic=best["aic"],
    )
    return result, comparison


def fit_severity_lognormal(severities: np.ndarray) -> dict:
    """Ajusta Lognormal à severidade individual por evento e retorna média,
    mediana e parâmetros — a mediana da Lognormal é sistematicamente menor que
    a média (assimetria positiva), o que deve ser destacado na comunicação de
    resultado (evita interpretar a média como "o sinistro típico")."""
    severities = np.asarray(severities, dtype=float)
    severities = severities[severities > 0]
    shape, loc, scale = stats.lognorm.fit(severities, floc=0)
    mean = stats.lognorm.mean(shape, loc=loc, scale=scale)
    median = stats.lognorm.median(shape, loc=loc, scale=scale)
    return {
        "shape": shape,
        "loc": loc,
        "scale": scale,
        "distribution_mean": float(mean),
        "distribution_median": float(median),
        "empirical_mean": float(severities.mean()),
        "empirical_median": float(np.median(severities)),
    }
