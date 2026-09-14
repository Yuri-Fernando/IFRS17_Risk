"""
Stress testing da provisão de ECL.

Aplica choques macroeconômicos (aumento de PD, aumento de LGD downturn) e
recalcula a ECL da carteira, permitindo avaliar sensibilidade de capital
e provisão a cenários adversos — prática exigida em exercícios de stress
test regulatório (BACEN, EBA) e mencionada como atividade típica de um
Data Scientist de risco de crédito ("avaliações técnicas de impacto
financeiro e regulatório").
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.modeling.lgd_model import estimate_lgd


SCENARIOS = {
    "base": {"pd_multiplier": 1.00, "lgd_downturn_addon": 0.00, "label": "Cenário Base"},
    "moderado": {"pd_multiplier": 1.30, "lgd_downturn_addon": 0.05, "label": "Estresse Moderado (+30% PD, +5pp LGD)"},
    "severo": {"pd_multiplier": 1.80, "lgd_downturn_addon": 0.12, "label": "Estresse Severo (+80% PD, +12pp LGD)"},
    "extremo": {"pd_multiplier": 2.50, "lgd_downturn_addon": 0.20, "label": "Estresse Extremo (+150% PD, +20pp LGD)"},
}


def run_stress_scenario(df_ecl: pd.DataFrame, pd_multiplier: float, lgd_downturn_addon: float, seed: int = 11) -> dict:
    stressed = df_ecl.copy()

    pd_used_stressed = np.clip(stressed["pd_used"].values * pd_multiplier, 0, 1)
    lgd_stressed = estimate_lgd(stressed, downturn_addon=lgd_downturn_addon, seed=seed)

    stressed["pd_used"] = pd_used_stressed
    stressed["lgd"] = lgd_stressed
    stressed["ecl"] = stressed["pd_used"] * stressed["lgd"] * stressed["ead"]

    return {
        "total_exposure": float(stressed["ead"].sum()),
        "total_ecl": float(stressed["ecl"].sum()),
        "coverage_ratio": float(stressed["ecl"].sum() / stressed["ead"].sum()),
        "avg_pd": float(stressed["pd_used"].mean()),
        "avg_lgd": float(stressed["lgd"].mean()),
    }


def run_all_scenarios(df_ecl: pd.DataFrame) -> pd.DataFrame:
    rows = []
    base_ecl = None
    for key, params in SCENARIOS.items():
        result = run_stress_scenario(df_ecl, params["pd_multiplier"], params["lgd_downturn_addon"])
        result["scenario"] = key
        result["label"] = params["label"]
        if key == "base":
            base_ecl = result["total_ecl"]
        result["ecl_delta_vs_base"] = result["total_ecl"] - base_ecl if base_ecl is not None else 0.0
        result["ecl_delta_pct"] = (result["ecl_delta_vs_base"] / base_ecl) if base_ecl else 0.0
        rows.append(result)
    return pd.DataFrame(rows)
