"""ECL lifetime com term structure de PD, cenários e decomposição (waterfall).

ECL_i = Σ_k q_i,k · LGD_i · EAD_i,k · DF_i,k   (k = meses; DF pela taxa efetiva)
- Stage 1: horizonte de 12 meses (ou prazo remanescente, se menor);
- Stage 2: vida remanescente (parcelado: prazo; rotativo: 36 meses de vida
  comportamental — premissa, IFRS 9 §5.5.20);
- Stage 3: workouts abertos, PD = 1, EAD no default.
q_i,k: contratos em dia → Kaplan-Meier por rating condicionado ao MOB atual;
contratos em atraso (D30/D60) → cadeia de Markov a partir do estado atual.
Staging: D30/D60 (backstop de 30 DPD) ou SICR (PD 12m PIT ≥ 2× PD 12m na
originação e ≥ +0,5 p.p.).
"""

from __future__ import annotations

import numpy as np
import pandas as pd

from src.modeling.lgd_ead_advanced import ead_profile
from src.modeling.macro_pit import vasicek_pit
from src.modeling.vintage_migration import markov_lifetime_pd

REVOLVING_LIFE = 36


def km_hazards(km_by_grade: dict[str, pd.DataFrame], max_mob: int) -> dict[str, np.ndarray]:
    """Hazard mensal por rating a partir do KM; cauda (MOB além do observado)
    usa a média dos últimos 12 meses observados — extrapolação documentada."""
    out = {}
    for g, km in km_by_grade.items():
        S = np.concatenate([[1.0], km["survival"].to_numpy()])
        h = np.where(S[:-1] > 0, 1 - S[1:] / S[:-1], 0.0)
        tail = h[-12:].mean() if len(h) >= 12 else h.mean()
        out[g] = np.concatenate([h, np.full(max(0, max_mob - len(h)), tail)])
    return out


def pit_adjust_monthly(h: np.ndarray, z_by_year: np.ndarray, rho: float) -> np.ndarray:
    """Converte hazard mensal TTC em PIT ano a ano (Vasicek sobre a PD anual condicional)."""
    out = h.copy()
    for y in range(int(np.ceil(len(h) / 12))):
        z = z_by_year[y] if y < len(z_by_year) else 0.0
        seg = slice(12 * y, 12 * (y + 1))
        p_ann = 1 - (1 - h[seg]) ** 12
        p_pit = vasicek_pit(p_ann, np.full_like(p_ann, z), rho)
        out[seg] = 1 - (1 - p_pit) ** (1 / 12)
    return out


def marginal_from_hazard(h: np.ndarray) -> np.ndarray:
    S = np.cumprod(1 - h)
    S_prev = np.concatenate([[1.0], S[:-1]])
    return S_prev * h


def assign_stage(book: pd.DataFrame, pd12_now: np.ndarray) -> np.ndarray:
    sicr = (pd12_now >= 2 * book["pd_12m_at_origination"].to_numpy()) & (
        pd12_now - book["pd_12m_at_origination"].to_numpy() >= 0.005)
    dpd = book["final_state"].isin(["D30", "D60"]).to_numpy()
    return np.where(dpd | sicr, 2, 1)


def compute_ecl(book: pd.DataFrame, hazards: dict, P_markov: dict, lgd: dict, ccf: float, rho: float,
                z_by_year: np.ndarray | None, lifetime_for_stage2: bool = True, use_pit: bool = True,
                force_stage1: bool = False, lgd_key: str = "lgd") -> pd.DataFrame:
    rows = []
    for _, r in book.iterrows():
        remaining = (int(r["term_months"]) - int(r["mob_now"])) if r["product"] == "installment" else REVOLVING_LIFE
        remaining = max(remaining, 1)
        mob = int(r["mob_now"])
        if r["final_state"] in ("D30", "D60"):
            cum = markov_lifetime_pd(P_markov[r["product"]], remaining, start=r["final_state"])
            q = np.diff(np.concatenate([[0.0], cum]))
        else:
            h = hazards[r["grade"]][mob: mob + remaining]
            if use_pit and z_by_year is not None:
                h = pit_adjust_monthly(h, z_by_year, rho)
            q = marginal_from_hazard(h)
        pd12 = float(q[:12].sum())
        rows.append({"loan_id": r["loan_id"], "q": q, "pd_12m_now": pd12, "remaining": remaining})
    tmp = pd.DataFrame(rows).set_index("loan_id")
    b = book.set_index("loan_id").join(tmp)
    stage = np.ones(len(b), dtype=int) if force_stage1 else assign_stage(b.reset_index(), b["pd_12m_now"].to_numpy())
    ecl, pd_used = [], []
    for (lid, r), st in zip(b.iterrows(), stage):
        H = len(r["q"]) if (st == 2 and lifetime_for_stage2) else min(12, len(r["q"]))
        ead = ead_profile(r, H, ccf)
        df = (1 + r["eir_annual"]) ** (-np.arange(1, H + 1) / 12)
        L = lgd["secured" if r["secured"] else "unsecured"][lgd_key]
        ecl.append(float(np.sum(r["q"][:H] * L * ead * df)))
        pd_used.append(float(r["q"][:H].sum()))
    b = b.reset_index()
    b["stage"], b["ecl"], b["pd_horizon"] = stage, ecl, pd_used
    b["ead_now"] = [ead_profile(r, 1, ccf)[0] for _, r in b.iterrows()]
    return b.drop(columns=["q"])


def stage3_ecl(open_defaults: pd.DataFrame, lgd: dict, lgd_key: str = "lgd") -> float:
    L = np.where(open_defaults["secured"], lgd["secured"][lgd_key], lgd["unsecured"][lgd_key])
    return float(np.sum(L * open_defaults["ead"]))


def weighted_ecl(results: dict[str, float], weights: dict[str, float]) -> float:
    return float(sum(weights[k] * v for k, v in results.items()))
