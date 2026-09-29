"""PIT × TTC e cenários macroeconômicos forward-looking (IFRS 9 §5.5.17(c), B5.5.42).

- TTC: PD média de longo prazo por rating (KM 12m ao longo do ciclo inteiro).
- Modelo satélite: Φ⁻¹(taxa de default anualizada do mês) = a + b·desemprego + c·PIB.
  Daí extrai-se o fator sistêmico implícito Ẑ_t (Vasicek com ρ).
- PIT: PD_PIT = Φ((Φ⁻¹(PD_TTC) − √ρ·Ẑ)/√(1−ρ)).
- Cenários base/upside/downside (3 anos) → Ẑ por ano → curva de PD PIT → ECL
  por cenário → ECL ponderada. Como a perda é convexa no fator, a ECL
  ponderada tende a superar a ECL do cenário base (não-linearidade exigida
  pela norma: não basta usar um cenário central).
Não há calibração regulatória real: dados e cenários são sintéticos.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
import statsmodels.api as sm
from scipy.stats import norm

SCENARIOS = {  # trajetórias anuais (ano 1..3) — premissas ilustrativas
    "base": {"weight": 0.50, "unemployment": [8.2, 8.0, 7.9], "gdp_growth": [2.0, 2.2, 2.3],
             "policy_rate": [10.5, 10.0, 9.5], "inflation": [4.5, 4.0, 3.8]},
    "upside": {"weight": 0.20, "unemployment": [7.5, 7.0, 6.8], "gdp_growth": [3.2, 3.0, 2.8],
               "policy_rate": [9.5, 9.0, 8.5], "inflation": [3.8, 3.5, 3.5]},
    "downside": {"weight": 0.30, "unemployment": [10.5, 11.5, 10.0], "gdp_growth": [-1.5, -0.5, 1.0],
                 "policy_rate": [13.0, 13.5, 12.0], "inflation": [6.5, 6.0, 5.0]},
}


def vasicek_pit(pd_ttc, Z, rho: float) -> np.ndarray:
    p = np.clip(np.asarray(pd_ttc, dtype=float), 1e-6, 0.999)
    return norm.cdf((norm.ppf(p) - np.sqrt(rho) * np.asarray(Z)) / np.sqrt(1 - rho))


def fit_satellite(delinq: pd.DataFrame, macro: pd.DataFrame, min_active: int = 500) -> dict:
    """Regressão de Φ⁻¹(DR anualizada) em macro, só em meses com carteira suficiente."""
    d = delinq.merge(macro, on="month")
    d = d[(d["active"] >= min_active) & (d["default_rate_monthly"] > 0)].copy()
    dr_annual = 1 - (1 - d["default_rate_monthly"]) ** 12
    d["probit_dr"] = norm.ppf(dr_annual.clip(1e-4, 0.999))
    X = sm.add_constant(d[["unemployment", "gdp_growth"]])
    m = sm.OLS(d["probit_dr"], X).fit(cov_type="HAC", cov_kwds={"maxlags": 3})
    return {"params": m.params.to_dict(), "bse": m.bse.to_dict(), "r2": float(m.rsquared), "n_months": int(len(d)),
            "fitted_probit_mean": float(m.fittedvalues.mean()), "resid_sd": float(np.std(m.resid)),
            "model": m}


def implied_z(sat: dict, unemployment, gdp_growth, rho: float) -> np.ndarray:
    """Converte o probit previsto em fator Ẑ relativo à média do ciclo observado."""
    p = sat["params"]
    probit = p["const"] + p["unemployment"] * np.asarray(unemployment) + p["gdp_growth"] * np.asarray(gdp_growth)
    # Φ⁻¹(PD_PIT) = (Φ⁻¹(PD) − √ρ Z)/√(1−ρ) ⇒ variação de probit ↔ −√ρ/√(1−ρ)·ΔZ
    return -(probit - sat["fitted_probit_mean"]) * np.sqrt(1 - rho) / np.sqrt(rho)


def scenario_z(sat: dict, rho: float, scenarios: dict = SCENARIOS) -> dict:
    return {k: implied_z(sat, v["unemployment"], v["gdp_growth"], rho) for k, v in scenarios.items()}


def pit_term_structure(marginal_ttc: np.ndarray, z_years: np.ndarray, rho: float) -> np.ndarray:
    """Ajusta PDs condicionais anuais TTC para PIT ano a ano (ano > 3 usa Ẑ=0 — reversão à média)."""
    cond = np.asarray(marginal_ttc, dtype=float)
    z = np.concatenate([z_years, np.zeros(max(0, len(cond) - len(z_years)))])[: len(cond)]
    return vasicek_pit(cond, z, rho)
