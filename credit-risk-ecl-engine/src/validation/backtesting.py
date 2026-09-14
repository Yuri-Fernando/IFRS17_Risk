"""
Backtesting de PD — Teste de Kupiec (Proportion of Failures).

Verifica se a taxa de default observada é estatisticamente compatível com
a PD média prevista pelo modelo, sob H0: taxa observada = PD prevista.
Amplamente usado em backtesting de modelos IRB/PD (Basileia) e citado nas
diretrizes de validação de modelos de crédito.
"""

from __future__ import annotations

import numpy as np
from scipy import stats


def kupiec_pof_test(n_observations: int, n_defaults: int, pd_predicted: float, confidence: float = 0.95) -> dict:
    """Teste de razão de verossimilhança de Kupiec (POF).

    Retorna a estatística LR, o p-valor e a decisão (aceita/rejeita H0).
    """
    raw_observed_rate = n_defaults / n_observations if n_observations else 0.0
    # Clipa a taxa observada para evitar log(0) nos casos-limite (0% ou
    # 100% de default, como ocorre por definição no Stage 3, onde todo
    # contrato já é inadimplente).
    observed_rate = float(np.clip(raw_observed_rate, 1e-6, 1 - 1e-6))

    p = np.clip(pd_predicted, 1e-6, 1 - 1e-6)
    x = n_defaults
    n = n_observations

    log_l0 = x * np.log(p) + (n - x) * np.log(1 - p)
    log_l1 = x * np.log(observed_rate) + (n - x) * np.log(1 - observed_rate)

    lr_stat = -2 * (log_l0 - log_l1)
    p_value = 1 - stats.chi2.cdf(lr_stat, df=1)

    critical_value = stats.chi2.ppf(confidence, df=1)
    reject_h0 = lr_stat > critical_value

    return {
        "n_observations": n_observations,
        "n_defaults": n_defaults,
        "observed_default_rate": float(observed_rate),
        "predicted_pd": float(pd_predicted),
        "lr_statistic": float(lr_stat),
        "p_value": float(p_value),
        "critical_value": float(critical_value),
        "reject_h0": bool(reject_h0),
        "conclusion": (
            "Modelo REJEITADO no backtesting (PD prevista diverge da taxa observada)"
            if reject_h0
            else "Modelo ACEITO no backtesting (PD prevista compatível com a taxa observada)"
        ),
    }


def backtest_by_stage(df_ecl) -> list[dict]:
    results = []
    for stage in sorted(df_ecl["stage"].unique()):
        subset = df_ecl[df_ecl["stage"] == stage]
        result = kupiec_pof_test(
            n_observations=len(subset),
            n_defaults=int(subset["default"].sum()),
            pd_predicted=float(subset["pd_used"].mean()),
        )
        result["stage"] = int(stage)
        results.append(result)
    return results
