"""Vintage analysis e matriz de migração de atraso (Current → 30 → 60 → Default, com cura).

- Vintage: default acumulado por safra (mês de originação) × MOB, sobre o
  número de contratos originados (curva "marginal por safra" → acumulada).
- Delinquency por mês calendário (30+ DPD / contratos ativos).
- Matriz de migração mensal estimada por contagem (estados C, D30, D60 →
  C, D30, D60, DEF, EXIT); DEF e EXIT absorventes.
- Lifetime PD via cadeia de Markov: P(DEF em n) = (Pⁿ)[C, DEF]; permite
  comparar com Kaplan-Meier e alimentar staging (30 DPD = backstop de SICR).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

MARKOV_STATES = ["C", "D30", "D60", "DEF", "EXIT"]


def vintage_curves(loans: pd.DataFrame, max_mob: int = 36) -> pd.DataFrame:
    """Default acumulado por safra trimestral × MOB (só MOBs observáveis para a safra)."""
    L = loans.copy()
    L["cohort"] = L["vintage"].dt.asfreq("Q").astype(str)
    last_month = int(L["exit_month"].max())
    rows = []
    for cohort, g in L.groupby("cohort"):
        n = len(g)
        mob_def = (g["default_month"] - g["orig_month"] + 1).where(g["event_default"] == 1)
        max_obs = int((last_month - g["orig_month"]).min()) + 1
        for mob in range(1, min(max_mob, max_obs) + 1):
            rows.append({"cohort": cohort, "mob": mob, "n_originated": n,
                         "cum_default_rate": float((mob_def <= mob).sum() / n)})
    return pd.DataFrame(rows)


def delinquency_by_month(panel: pd.DataFrame) -> pd.DataFrame:
    g = panel.groupby("month").agg(active=("state", "size"),
                                   dpd30_plus=("state", lambda s: int(s.isin(["D30", "D60"]).sum())),
                                   Z=("Z", "first"))
    g["dpd30_rate"] = g["dpd30_plus"] / g["active"]
    defaults = panel[panel["next_state"] == "DEF"].groupby("month").size()
    g["default_rate_monthly"] = (defaults.reindex(g.index, fill_value=0) / g["active"])
    return g.reset_index()


def transition_matrix(panel: pd.DataFrame, by: str | None = None) -> pd.DataFrame | dict:
    def _mat(df):
        c = pd.crosstab(df["state"], df["next_state"]).reindex(index=MARKOV_STATES[:3], columns=MARKOV_STATES,
                                                                fill_value=0)
        P = c.div(c.sum(axis=1), axis=0)
        full = pd.DataFrame(0.0, index=MARKOV_STATES, columns=MARKOV_STATES)
        full.loc[P.index, P.columns] = P.to_numpy()
        full.loc["DEF", "DEF"] = 1.0
        full.loc["EXIT", "EXIT"] = 1.0
        return full
    if by is None:
        return _mat(panel)
    return {k: _mat(g) for k, g in panel.groupby(by)}


def markov_lifetime_pd(P: pd.DataFrame, horizon: int, start: str = "C") -> np.ndarray:
    M = P.to_numpy()
    v = np.zeros(len(M))
    v[MARKOV_STATES.index(start)] = 1.0
    out = []
    for _ in range(horizon):
        v = v @ M
        out.append(v[MARKOV_STATES.index("DEF")])
    return np.array(out)


def roll_rates(P: pd.DataFrame) -> dict:
    return {"C_to_30": float(P.loc["C", "D30"]), "30_to_60": float(P.loc["D30", "D60"]),
            "60_to_default": float(P.loc["D60", "DEF"]), "cure_30": float(P.loc["D30", "C"]),
            "cure_60": float(P.loc["D60", "C"])}
