"""Painel sintético mensal de empréstimos com safras (vintages), MOB, DPD e macro.

Por que sintético: o German Credit (dataset real da v2) não tem data de
originação, histórico mensal, recuperações nem ciclo macro — requisitos para
survival analysis, vintage, matriz de migração, LGD de workout, CCF e PIT/TTC.
O gerador cria esse painel com mecanismos EXPLÍCITOS (verdade conhecida), para
que os estimadores sejam verificáveis. Nenhuma conclusão sobre carteira real.

Mecanismos:
- Macro mensal (desemprego, PIB, Selic, IPCA) com uma recessão sintética;
  fator sistêmico Z_t (padronizado; Z < 0 = ciclo adverso).
- PD TTC anual por rating (A–E) → PD PIT via Vasicek: Φ((Φ⁻¹(PD·s(MOB)) − √ρ·Z_t)/√(1−ρ)).
- Forma da hazard por MOB s(m) com pico perto de 12–18 meses (hazard não constante).
- Estados de atraso: Corrente → 30 → 60 → Default (90 DPD), com curas; saída por
  pré-pagamento ou vencimento.
- Parcelado (amortização Price, parte com garantia de veículo) e rotativo
  (cartão; utilização sobe antes do default → CCF).
- Workout: recuperações ao longo de 3–24 meses (garantia com haircut; sem
  garantia com recuperação parcial), descontadas pela taxa efetiva do contrato.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import norm

GRADES = ["A", "B", "C", "D", "E"]
PD_TTC = {"A": 0.010, "B": 0.025, "C": 0.050, "D": 0.100, "E": 0.200}
STATES = ["C", "D30", "D60", "DEF", "EXIT"]


@dataclass
class LoanPanel:
    loans: pd.DataFrame
    panel: pd.DataFrame
    defaults: pd.DataFrame
    macro: pd.DataFrame
    params: dict


def mob_shape(m: np.ndarray) -> np.ndarray:
    """Multiplicador de hazard por MOB: sobe até ~15 meses e decai (média ≈ 1 em 48 meses)."""
    m = np.maximum(np.asarray(m, dtype=float), 1.0)
    return 0.37 + 0.9 * (m / 15.0) * np.exp(1 - m / 15.0)


def generate_macro(n_months: int, seed: int) -> pd.DataFrame:
    rng = np.random.default_rng(seed)
    t = np.arange(n_months)
    recession = np.exp(-0.5 * ((t - 30) / 5.0) ** 2)  # choque centrado no mês 30
    u = 8.0 + 3.5 * recession + np.cumsum(rng.normal(0, 0.08, n_months)) * 0.3
    gdp = 2.0 - 5.0 * recession + rng.normal(0, 0.4, n_months)
    selic = 10.5 + 3.0 * np.roll(recession, -4) + rng.normal(0, 0.15, n_months)
    ipca = 4.5 + 2.0 * np.roll(recession, -6) + rng.normal(0, 0.2, n_months)
    z_u = (u - u.mean()) / u.std()
    z_g = (gdp - gdp.mean()) / gdp.std()
    Z = -(0.7 * z_u - 0.3 * z_g)
    Z = (Z - Z.mean()) / Z.std()
    return pd.DataFrame({"month": t, "unemployment": u, "gdp_growth": gdp, "policy_rate": selic,
                         "inflation": ipca, "Z": Z})


def pit_pd_annual(pd_ttc, Z, rho: float) -> np.ndarray:
    p = np.clip(pd_ttc, 1e-6, 0.999)
    return norm.cdf((norm.ppf(p) - np.sqrt(rho) * Z) / np.sqrt(1 - rho))


def generate_loan_panel(n_loans: int = 8000, n_cohorts: int = 30, n_months: int = 54, rho: float = 0.12,
                        seed: int = 2026) -> LoanPanel:
    rng = np.random.default_rng(seed)
    macro = generate_macro(n_months, seed + 1)
    Z = macro["Z"].to_numpy()

    grade = rng.choice(GRADES, size=n_loans, p=[0.25, 0.30, 0.25, 0.13, 0.07])
    pd_ttc = np.array([PD_TTC[g] for g in grade])
    orig = rng.integers(0, n_cohorts, n_loans)
    product = np.where(rng.random(n_loans) < 0.6, "installment", "revolving")
    inst = product == "installment"
    term = np.where(inst, rng.choice([24, 36, 48], n_loans), 999)
    amount = np.where(inst, rng.lognormal(np.log(25000), 0.5, n_loans), 0.0)
    limit = np.where(~inst, rng.lognormal(np.log(8000), 0.6, n_loans), 0.0)
    secured = inst & (rng.random(n_loans) < 0.5)
    ltv = np.where(secured, rng.uniform(0.5, 0.95, n_loans), np.nan)
    collateral = np.where(secured, amount / np.nan_to_num(ltv, nan=1.0), 0.0)
    eir_annual = np.where(inst, 0.18 + 1.5 * pd_ttc, 0.60 + 1.0 * pd_ttc)  # taxa efetiva anual
    r_m = (1 + eir_annual) ** (1 / 12) - 1
    pmt = np.where(inst, amount * r_m / (1 - (1 + r_m) ** (-np.minimum(term, 600))), 0.0)
    util0 = rng.beta(2, 3, n_loans)

    loans = pd.DataFrame({
        "loan_id": [f"L{i:06d}" for i in range(n_loans)], "grade": grade, "pd_ttc": pd_ttc, "product": product,
        "orig_month": orig, "vintage": pd.Period("2022-01", "M") + orig, "term_months": term,
        "amount": amount, "limit": limit, "secured": secured, "ltv": ltv, "collateral_value": collateral,
        "eir_annual": eir_annual,
        "pd_12m_at_origination": pit_pd_annual(pd_ttc, Z[orig], rho),
    })

    state = np.full(n_loans, -1)  # -1 = ainda não originado
    balance = np.zeros(n_loans)
    drawn = np.zeros(n_loans)
    drawn_hist = np.zeros((n_loans, n_months))
    default_month = np.full(n_loans, -1)
    exit_month = np.full(n_loans, -1)
    rows = []
    roll = {"D30_D60": 0.50, "D60_DEF": 0.60, "D30_C": 0.40, "D60_C": 0.25}
    for t in range(n_months):
        new = orig == t
        state[new] = 0
        balance[new] = amount[new]
        drawn[new] = limit[new] * util0[new]
        active = state >= 0
        mob = np.where(active, t - orig + 1, 0)
        pd_pit = pit_pd_annual(pd_ttc * mob_shape(mob), Z[t], rho)
        h = 1 - (1 - pd_pit) ** (1 / 12)
        # entrada em atraso calibrada pela probabilidade de absorção em default a
        # partir de D30 (com curas): P = r30_60·r60_def / [(1−s30)(1−s60)]
        p_abs = (roll["D30_D60"] * roll["D60_DEF"]
                 / ((1 - (1 - roll["D30_D60"] - roll["D30_C"])) * (1 - (1 - roll["D60_DEF"] - roll["D60_C"]))))
        p_c30 = np.clip(h / p_abs, 0, 0.5)
        u = rng.random(n_loans)
        nxt = state.copy()
        c, d30, d60 = state == 0, state == 1, state == 2
        prepay = 0.012 * inst + 0.006 * (~inst)
        nxt[c & (u < p_c30)] = 1
        nxt[c & (u >= p_c30) & (u < p_c30 + prepay)] = 4
        nxt[d30 & (u < roll["D30_D60"])] = 2
        nxt[d30 & (u >= roll["D30_D60"]) & (u < roll["D30_D60"] + roll["D30_C"])] = 0
        nxt[d60 & (u < roll["D60_DEF"])] = 3
        nxt[d60 & (u >= roll["D60_DEF"]) & (u < roll["D60_DEF"] + roll["D60_C"])] = 0
        # amortização (parcelado em dia) e utilização (rotativo sobe quando em atraso)
        paying = inst & (nxt == 0) & (state >= 0)
        interest = balance * r_m
        balance = np.where(paying, np.maximum(balance + interest - pmt, 0.0), np.where(inst & (nxt >= 1) & (nxt <= 2),
                                                                                      balance + interest, balance))
        rev = (~inst) & (state >= 0) & (nxt < 3)
        drift = np.where(nxt >= 1, 0.08, rng.normal(0, 0.03, n_loans))
        drawn = np.where(rev, np.clip(drawn + limit * drift, 0, limit), drawn)
        matured = inst & (nxt == 0) & (mob >= term)
        nxt[matured | (inst & (balance <= 1) & (nxt == 0) & (state >= 0))] = 4
        newly_def = (nxt == 3) & (state != 3)
        default_month[newly_def] = t
        newly_exit = (nxt == 4) & (state != 4)
        exit_month[newly_exit] = t
        drawn_hist[:, t] = drawn
        live = state >= 0
        live_rows = np.where(live & (state != 3) & (state != 4))[0]
        rows.append(pd.DataFrame({"loan_id": loans["loan_id"].to_numpy()[live_rows], "month": t,
                                  "mob": mob[live_rows], "state": np.array(STATES)[state[live_rows]],
                                  "next_state": np.array(STATES)[nxt[live_rows]],
                                  "balance": np.where(inst[live_rows], balance[live_rows], drawn[live_rows]),
                                  "Z": Z[t]}))
        state = nxt

    panel = pd.concat(rows, ignore_index=True)

    # ---- default: EAD, CCF e workout ----
    d = np.where(default_month >= 0)[0]
    tdef = default_month[d]
    ead = np.where(inst[d], balance[d], drawn[d])
    back = np.clip(tdef - 12, 0, None)
    drawn_12 = np.where(~inst[d], drawn_hist[d, back], np.nan)
    workout = rng.integers(3, 25, len(d))
    rec_rate = np.where(secured[d], np.minimum(collateral[d] * rng.uniform(0.55, 0.85, len(d)) / np.maximum(ead, 1), 1.0),
                        rng.beta(2, 6, len(d)))
    downturn_hit = Z[tdef] < -0.8
    rec_rate = rec_rate * np.where(downturn_hit, 0.8, 1.0)  # recuperação pior em recessão
    costs = 0.05 * ead
    disc = (1 + eir_annual[d]) ** (-workout / 12)
    pv_rec = rec_rate * ead * disc - costs * disc
    lgd = np.clip(1 - pv_rec / np.maximum(ead, 1), 0, 1)
    closed = tdef + workout <= n_months - 1
    defaults = pd.DataFrame({
        "loan_id": loans["loan_id"].to_numpy()[d], "default_month": tdef, "product": product[d], "grade": grade[d],
        "secured": secured[d], "ltv": ltv[d], "ead": ead, "limit": limit[d], "drawn_12m_before": drawn_12,
        "workout_months": workout, "recovery_rate_nominal": rec_rate, "realized_lgd": lgd, "workout_closed": closed,
        "Z_at_default": Z[tdef], "eir_annual": eir_annual[d]})

    loans["default_month"] = default_month
    loans["exit_month"] = exit_month
    last = n_months - 1
    end = np.where(default_month >= 0, default_month, np.where(exit_month >= 0, exit_month, last))
    loans["duration_months"] = np.maximum(end - orig + 1, 1)
    loans["event_default"] = (default_month >= 0).astype(int)
    loans["final_state"] = np.array(STATES)[np.clip(state, 0, 4)]
    loans["final_balance"] = np.where(inst, balance, drawn)
    return LoanPanel(loans, panel, defaults, macro, {"rho": rho, "roll_rates": roll, "seed": seed,
                                                     "n_months": n_months, "pd_ttc": PD_TTC})
