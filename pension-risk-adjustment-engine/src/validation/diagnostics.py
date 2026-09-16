"""
Diagnósticos e validação estatística — testes de aderência, autocorrelação e
verificação de consistência interna do dataset sintético (o A/E agregado deve
aproximar 100% quando calculado contra a MESMA tábua usada para gerar os
sinistros, ver src/data/synthetic_portfolio.py).
"""
from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats


def chi_square_ae_test(observed_events: float, expected_events: float, n_cells: int = 1) -> dict:
    """Teste qui-quadrado simples de aderência observado vs. esperado — réplica
    da verificação feita no projeto original quando o A/E ficou muito distante
    de 100% (metodologia, seção 6, gap #6)."""
    if expected_events <= 0:
        return {"chi2_statistic": float("nan"), "p_value": float("nan"), "significant": None}
    chi2_stat = (observed_events - expected_events) ** 2 / expected_events
    p_value = 1 - stats.chi2.cdf(chi2_stat, df=max(n_cells - 1, 1))
    return {
        "chi2_statistic": float(chi2_stat),
        "p_value": float(p_value),
        "significant": bool(p_value < 0.05),
        "interpretation": (
            "Diferença estatisticamente significativa entre observado e esperado — investigar tábua/exposição."
            if p_value < 0.05
            else "Sem evidência de diferença significativa entre observado e esperado."
        ),
    }


def autocorrelation_check(series: np.ndarray, lags: tuple[int, ...] = (1, 12)) -> pd.DataFrame:
    """Autocorrelação da série de sinistralidade mensal em lags de interesse
    (mês consecutivo e mesmo mês do ano anterior) — replica o diagnóstico
    temporal feito no projeto original para verificar se a sinistralidade é
    dirigida por oscilação aleatória ou por tendência/sazonalidade."""
    series = pd.Series(series).dropna()
    rows = []
    for lag in lags:
        if len(series) <= lag:
            rows.append({"lag": lag, "autocorrelation": float("nan")})
            continue
        ac = series.autocorr(lag=lag)
        rows.append({"lag": lag, "autocorrelation": ac})
    return pd.DataFrame(rows)


def internal_consistency_check(observed_events: float, expected_events: float, tolerance: float = 0.25) -> dict:
    """Verifica que o dataset sintético é internamente consistente: como os
    sinistros foram gerados por sorteio Bernoulli usando a própria tábua base,
    o A/E agregado deve estar próximo de 100% (dentro de uma tolerância que
    reflete o ruído amostral esperado)."""
    ae = observed_events / expected_events if expected_events else float("nan")
    within_tolerance = abs(ae - 1.0) <= tolerance
    return {
        "ae_ratio": ae,
        "within_tolerance": bool(within_tolerance),
        "tolerance": tolerance,
        "interpretation": (
            f"A/E = {ae:.1%} está dentro da tolerância de +/-{tolerance:.0%} do esperado (100%) — "
            "dataset sintético consistente com a tábua geradora."
            if within_tolerance
            else f"A/E = {ae:.1%} fora da tolerância — revisar geração do dataset sintético."
        ),
    }
