"""Validation pack automático (Model Risk Management).

Seções: discriminação, calibração (binomial exato + Jeffreys por rating),
estabilidade (PSI de mix de rating entre safras), backtesting por safra
(PD prevista na originação × default observado em 12m, semáforo),
benchmarking (KM × Cox × Weibull × Markov × fórmula simples), sensibilidade
(pesos de cenário e ρ), limitações, inventário e status de aprovação.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist
from scipy.stats import binomtest
from sklearn.metrics import roc_auc_score, roc_curve


def twelve_month_outcomes(loans: pd.DataFrame, last_month: int) -> pd.DataFrame:
    """Contratos com 12 meses observáveis após a originação (ou default antes)."""
    L = loans.copy()
    L["def_12m"] = ((L["event_default"] == 1) & (L["default_month"] - L["orig_month"] + 1 <= 12)).astype(int)
    exited_early = (L["exit_month"] >= 0) & (L["exit_month"] - L["orig_month"] + 1 < 12) & (L["def_12m"] == 0)
    observable = (last_month - L["orig_month"] + 1 >= 12) & ~exited_early
    return L[observable]


def discrimination(y, p) -> dict:
    auc = roc_auc_score(y, p)
    fpr, tpr, _ = roc_curve(y, p)
    return {"auc": float(auc), "gini": float(2 * auc - 1), "ks": float(np.max(tpr - fpr)), "n": int(len(y))}


def calibration_by_grade(obs: pd.DataFrame, pd_col: str) -> pd.DataFrame:
    rows = []
    for g, d in obs.groupby("grade"):
        n, k = len(d), int(d["def_12m"].sum())
        p = float(d[pd_col].mean())
        test = binomtest(k, n, p)
        lo, hi = beta_dist.ppf([0.025, 0.975], k + 0.5, n - k + 0.5)
        rows.append({"grade": g, "n": n, "defaults": k, "predicted_pd": p, "observed_dr": k / n,
                     "jeffreys_low": float(lo), "jeffreys_high": float(hi), "binomial_p": float(test.pvalue),
                     "result": "ok" if lo <= p <= hi else ("subestima" if p < lo else "superestima")})
    return pd.DataFrame(rows)


def vintage_backtest(obs: pd.DataFrame, pd_col: str) -> pd.DataFrame:
    o = obs.assign(cohort=obs["vintage"].dt.asfreq("Q").astype(str))
    g = o.groupby("cohort").agg(n=("def_12m", "size"), observed=("def_12m", "mean"), predicted=(pd_col, "mean"))
    g["ratio_obs_pred"] = g["observed"] / g["predicted"]
    g["traffic_light"] = np.select([g["ratio_obs_pred"].between(0.8, 1.25), g["ratio_obs_pred"].between(0.6, 1.6)],
                                   ["green", "amber"], "red")
    return g.reset_index()


def grade_psi(early: pd.Series, late: pd.Series) -> float:
    cats = sorted(set(early) | set(late))
    e = np.array([(early == c).mean() for c in cats]).clip(1e-4)
    a = np.array([(late == c).mean() for c in cats]).clip(1e-4)
    return float(np.sum((a - e) * np.log(a / e)))


def render_markdown(pack: dict) -> str:
    def tbl(df: pd.DataFrame) -> str:
        def fmt(v):
            return f"{v:.4f}" if isinstance(v, (float, np.floating)) else str(v)
        head = "| " + " | ".join(map(str, df.columns)) + " |"
        sep = "|" + "---|" * len(df.columns)
        body = ["| " + " | ".join(fmt(v) for v in row) + " |" for row in df.itertuples(index=False)]
        return "\n".join([head, sep, *body])

    lines = [
        "# Validation Pack — Credit Risk ECL Engine · extensão lifetime/forward-looking",
        "",
        f"Gerado automaticamente por `run_lifetime_pipeline.py` em {pack['generated_at']}. "
        "**Dados sintéticos** (`src/data/panel.py`) — valida o software e o método, não uma carteira real.",
        "",
        "## 1. Inventário e status",
        tbl(pd.DataFrame(pack["inventory"])),
        "",
        "## 2. Discriminação (PD 12m na originação × default em 12 meses)",
        tbl(pd.DataFrame([pack["discrimination"]])),
        "",
        "## 3. Calibração por rating (binomial exato, IC de Jeffreys 95%)",
        tbl(pack["calibration"]),
        "",
        "## 4. Estabilidade",
        f"PSI do mix de rating (safras 2022 × 2023): **{pack['stability']['grade_mix_psi']:.4f}**",
        "",
        "## 5. Backtesting por safra (semáforo: verde 0,8–1,25 · âmbar 0,6–1,6 · vermelho fora)",
        tbl(pack["vintage_backtest"]),
        "",
        "## 6. Benchmarking de lifetime PD (carteira, meses desde a originação)",
        tbl(pack["benchmark"]),
        "",
        "## 7. Sensibilidade da ECL",
        tbl(pack["sensitivity"]),
        "",
        "## 8. Limitações",
        *[f"- {x}" for x in pack["limitations"]],
        "",
        "## 9. Conclusão do validador (automática — requer revisão humana)",
        pack["conclusion"],
    ]
    return "\n".join(lines) + "\n"
