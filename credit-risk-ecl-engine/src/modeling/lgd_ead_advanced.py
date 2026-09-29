"""LGD de workout e EAD/CCF (IFRS 9 §5.5.17, B5.5.51–55).

LGD econômica = 1 − PV(recuperações − custos) / EAD, descontada pela taxa
efetiva do contrato ao longo do período de workout. Só workouts ENCERRADOS
entram na estimação; workouts abertos são contados e reportados (viés de
resolução: recuperações lentas/ruins ficam de fora — declarado).
Segmentação: com/sem garantia e faixa de LTV. Downturn LGD = LGD média dos
defaults ocorridos em ciclo adverso (Z < −0,8) comparada à média.

EAD: parcelado = saldo da tabela Price no mês; rotativo = sacado + CCF ×
(limite − sacado), com CCF = (EAD − sacado₁₂) / (limite − sacado₁₂)
estimado nos defaults (clip [0, 1]).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def lgd_segments(defaults: pd.DataFrame, downturn_z: float = -0.8) -> dict:
    d = defaults.copy()
    closed = d[d["workout_closed"]]
    d_ltv = pd.cut(closed["ltv"], [0, 0.7, 0.85, 1.0], labels=["LTV≤70%", "70–85%", ">85%"])
    closed = closed.assign(segment=np.where(closed["secured"], "garantido " + d_ltv.astype(str), "sem garantia"))
    seg = closed.groupby("segment")["realized_lgd"].agg(["count", "mean", "std"]).reset_index()
    base_sec = closed.loc[closed["secured"], "realized_lgd"].mean()
    base_uns = closed.loc[~closed["secured"], "realized_lgd"].mean()
    dt = closed[closed["Z_at_default"] < downturn_z]
    down_sec = dt.loc[dt["secured"], "realized_lgd"].mean()
    down_uns = dt.loc[~dt["secured"], "realized_lgd"].mean()
    return {
        "by_segment": seg,
        "secured": {"lgd": float(base_sec), "downturn_lgd": float(down_sec), "n_downturn": int(dt["secured"].sum())},
        "unsecured": {"lgd": float(base_uns), "downturn_lgd": float(down_uns), "n_downturn": int((~dt["secured"]).sum())},
        "n_closed": int(len(closed)), "n_open_workouts": int((~d["workout_closed"]).sum()),
        "resolution_bias_note": "workouts abertos excluídos; LGD pode estar subestimada se recuperações lentas forem piores",
    }


def workout_lgd(ead: float, recoveries: list[float], months: list[int], costs: list[float], eir_annual: float) -> float:
    """LGD econômica de um caso: fluxos descontados mensalmente à taxa efetiva."""
    r_m = (1 + eir_annual) ** (1 / 12) - 1
    pv = sum((rec - c) / (1 + r_m) ** m for rec, c, m in zip(recoveries, costs, months))
    return float(np.clip(1 - pv / ead, 0, 1))


def estimate_ccf(defaults: pd.DataFrame) -> dict:
    rev = defaults[(defaults["product"] == "revolving") & defaults["drawn_12m_before"].notna()].copy()
    undrawn = (rev["limit"] - rev["drawn_12m_before"]).clip(lower=1)
    ccf = ((rev["ead"] - rev["drawn_12m_before"]) / undrawn).clip(0, 1)
    return {"ccf_mean": float(ccf.mean()), "ccf_median": float(ccf.median()), "n": int(len(ccf)),
            "definition": "CCF = (EAD − sacado 12m antes) / (limite − sacado 12m antes), clip [0,1]"}


def amortizing_balance(principal: float, eir_annual: float, term: int, months_elapsed: int) -> float:
    r = (1 + eir_annual) ** (1 / 12) - 1
    if months_elapsed >= term:
        return 0.0
    pmt = principal * r / (1 - (1 + r) ** (-term))
    return float(principal * (1 + r) ** months_elapsed - pmt * ((1 + r) ** months_elapsed - 1) / r)


def ead_profile(row: pd.Series, horizon_months: int, ccf: float) -> np.ndarray:
    """EAD esperado no início de cada mês futuro (1..horizon)."""
    if row["product"] == "installment":
        elapsed = int(row["mob_now"])
        return np.array([amortizing_balance(row["amount"], row["eir_annual"], int(row["term_months"]), elapsed + k)
                         for k in range(horizon_months)])
    drawn = row["final_balance"]
    return np.full(horizon_months, drawn + ccf * max(row["limit"] - drawn, 0.0))
