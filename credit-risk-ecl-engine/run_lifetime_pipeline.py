#!/usr/bin/env python
"""Extensão v2.1 do Credit Risk ECL Engine — lifetime PD e forward-looking.

    python run_lifetime_pipeline.py          → reports/lifetime/ (JSON, CSV, figuras, validation_pack.md)

Fluxo: painel sintético → survival (KM, Cox, Weibull, incidência cumulativa)
→ term structure × fórmula simples → vintage e matriz de migração → satélite
macro, PIT/TTC e cenários → LGD de workout, downturn, CCF → PD bayesiana →
ECL lifetime por cenário e ponderada → waterfall de drivers → validation pack.
O pipeline original (German Credit, `run_pipeline.py`) permanece inalterado.
"""

from __future__ import annotations

import json
import sys
import time
from datetime import datetime, timezone
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt  # noqa: E402
import numpy as np  # noqa: E402
import pandas as pd  # noqa: E402

ROOT = Path(__file__).resolve().parent
sys.path.insert(0, str(ROOT))
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

from src.data.panel import GRADES, generate_loan_panel  # noqa: E402
from src.governance.audit_log import AuditLog  # noqa: E402
from src.modeling.bayesian_pd import beta_binomial_pd  # noqa: E402
from src.modeling.lgd_ead_advanced import estimate_ccf, lgd_segments  # noqa: E402
from src.modeling.lifetime_ecl import compute_ecl, km_hazards, stage3_ecl, weighted_ecl  # noqa: E402
from src.modeling.macro_pit import SCENARIOS, fit_satellite, scenario_z  # noqa: E402
from src.modeling.survival.survival_models import (cumulative_incidence, fit_cox, fit_weibull_aft,  # noqa: E402
                                                   kaplan_meier, simple_lifetime_pd, term_structure)
from src.modeling.vintage_migration import (delinquency_by_month, markov_lifetime_pd, roll_rates,  # noqa: E402
                                            transition_matrix, vintage_curves)
from src.validation.validation_pack import (calibration_by_grade, discrimination, grade_psi,  # noqa: E402
                                            render_markdown, twelve_month_outcomes, vintage_backtest)

OUT = ROOT / "reports" / "lifetime"


def _fig(name):
    plt.tight_layout()
    plt.savefig(OUT / "figures" / f"{name}.png", dpi=120)
    plt.close()


def _covariates(L: pd.DataFrame) -> pd.DataFrame:
    X = pd.get_dummies(L["grade"], prefix="grade", dtype=float).drop(columns="grade_A")
    X["revolving"] = (L["product"] == "revolving").astype(float)
    X["secured"] = L["secured"].astype(float)
    return X


def main(seed: int = 2026) -> dict:
    t0 = time.perf_counter()
    (OUT / "figures").mkdir(parents=True, exist_ok=True)
    audit = AuditLog()
    lp = generate_loan_panel(seed=seed)
    L, P, D, M = lp.loans, lp.panel, lp.defaults, lp.macro
    rho = lp.params["rho"]
    T = lp.params["n_months"] - 1
    audit.log("panel", n_loans=len(L), n_panel_rows=len(P), n_defaults=len(D), rho=rho)
    print(f"[1/9] painel: {len(L)} contratos, {len(P)} linhas mensais, {len(D)} defaults")

    # ---- 2. survival
    dur, ev = L["duration_months"].to_numpy(), L["event_default"].to_numpy()
    competing = ((L["exit_month"] >= 0) & (L["event_default"] == 0)).astype(int).to_numpy()
    km_all = kaplan_meier(dur, ev, 48)
    km_by_grade = {g: kaplan_meier(dur[L["grade"] == g], ev[L["grade"] == g], 54) for g in GRADES}
    cif = cumulative_incidence(dur, ev, competing, 48)
    X = _covariates(L)
    cox = fit_cox(X, dur, ev)
    wb = fit_weibull_aft(X, dur, ev)
    months = np.arange(1, 49)
    S_cox = cox.survival(X, months).mean(axis=0)
    S_wb = wb.survival(X, months).mean(axis=0)
    Pm = transition_matrix(P)
    P_by_product = {k: transition_matrix(P[P["loan_id"].isin(L.loc[L["product"] == k, "loan_id"])])
                    for k in ("installment", "revolving")}
    markov = markov_lifetime_pd(Pm, 48)
    pd12_km = float(km_all.loc[km_all["t"] == 12, "cum_pd"].iloc[0])
    bench = pd.DataFrame({
        "months": [12, 24, 36, 48],
        "kaplan_meier": [float(km_all.loc[km_all["t"] == m, "cum_pd"].iloc[0]) for m in (12, 24, 36, 48)],
        "cif_competing_risk": [float(cif.loc[cif["t"] == m, "cif_default"].iloc[0]) for m in (12, 24, 36, 48)],
        "cox_ph": [float(1 - S_cox[m - 1]) for m in (12, 24, 36, 48)],
        "weibull_aft": [float(1 - S_wb[m - 1]) for m in (12, 24, 36, 48)],
        "markov_chain": [float(markov[m - 1]) for m in (12, 24, 36, 48)],
        "simple_formula_v2": [float(simple_lifetime_pd(pd12_km, m)) for m in (12, 24, 36, 48)],
    })
    bench.to_csv(OUT / "lifetime_pd_benchmark.csv", index=False)
    ts = {g: term_structure(km["cum_pd"].to_numpy(), 4).assign(grade=g) for g, km in km_by_grade.items()}
    ts_df = pd.concat(ts.values())
    ts_df["simple_formula_cum"] = [simple_lifetime_pd(ts[g]["cumulative_pd"].iloc[0], 12 * y)
                                   for g, y in zip(ts_df["grade"], ts_df["year"])]
    ts_df.to_csv(OUT / "term_structure_by_grade.csv", index=False)
    cox.summary().to_csv(OUT / "cox_summary.csv", index=False)
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    for g, km in km_by_grade.items():
        ax[0].plot(km["t"], km["cum_pd"], label=f"KM {g}")
        ax[0].plot(km["t"], simple_lifetime_pd(ts[g]["cumulative_pd"].iloc[0], km["t"]), ls=":", c="grey")
    ax[0].set(title="PD acumulada por rating: KM (linha) × fórmula simples (pontilhado)", xlabel="MOB")
    ax[0].legend(fontsize=7)
    for c in bench.columns[1:]:
        ax[1].plot(bench["months"], bench[c], marker="o", label=c)
    ax[1].set(title="Benchmark de lifetime PD (carteira)", xlabel="meses")
    ax[1].legend(fontsize=7)
    _fig("lifetime_pd")
    audit.log("survival", pd12_km=pd12_km, cox_hr=cox.summary().set_index("covariate")["hazard_ratio"].round(3).to_dict(),
              weibull_shape=wb.shape)
    print(f"[2/9] survival: PD12 KM={pd12_km:.4f}; Weibull shape={wb.shape:.2f}; Cox HR(E)={np.exp(cox.params[3]):.1f}")

    # ---- 3. vintage & migração
    vint = vintage_curves(L)
    vint.to_csv(OUT / "vintage_curves.csv", index=False)
    delinq = delinquency_by_month(P)
    delinq.to_csv(OUT / "delinquency_by_month.csv", index=False)
    Pm.round(5).to_csv(OUT / "transition_matrix.csv")
    fig, ax = plt.subplots(1, 2, figsize=(12, 4.2))
    for c, g in vint.groupby("cohort"):
        ax[0].plot(g["mob"], g["cum_default_rate"], label=c)
    ax[0].set(title="Vintage: default acumulado por safra × MOB", xlabel="MOB")
    ax[0].legend(fontsize=6, ncol=2)
    ax[1].plot(delinq["month"], delinq["dpd30_rate"], label="30+ DPD")
    ax2 = ax[1].twinx()
    ax2.plot(delinq["month"], delinq["Z"], c="grey", ls="--", label="Z macro")
    ax[1].set(title="Atraso 30+ por mês calendário × fator macro", xlabel="mês")
    _fig("vintage_delinquency")
    print(f"[3/9] migração: {roll_rates(Pm)}")

    # ---- 4. macro / PIT
    sat = fit_satellite(delinq, M)
    zs = scenario_z(sat, rho)
    audit.log("satellite", params=sat["params"], r2=sat["r2"], scenario_z={k: v.round(3).tolist() for k, v in zs.items()})
    print(f"[4/9] satélite: R²={sat['r2']:.2f}, Z cenários={ {k: np.round(v, 2).tolist() for k, v in zs.items()} }")

    # ---- 5. LGD / EAD / Bayes
    lgd = lgd_segments(D)
    ccf = estimate_ccf(D)
    lgd["by_segment"].to_csv(OUT / "lgd_segments.csv", index=False)
    obs12 = twelve_month_outcomes(L, T)
    seg = obs12.assign(segment=obs12["grade"] + "·" + obs12["product"]).groupby("segment").agg(
        n=("def_12m", "size"), defaults=("def_12m", "sum")).reset_index()
    bayes = beta_binomial_pd(seg, "segment")
    bayes.to_csv(OUT / "bayesian_pd_by_segment.csv", index=False)
    print(f"[5/9] LGD garantido={lgd['secured']['lgd']:.3f} (downturn {lgd['secured']['downturn_lgd']:.3f}); "
          f"sem garantia={lgd['unsecured']['lgd']:.3f} (downturn {lgd['unsecured']['downturn_lgd']:.3f}); CCF={ccf['ccf_mean']:.3f}")

    # ---- 6. ECL lifetime por cenário
    book = L[L["final_state"].isin(["C", "D30", "D60"])].copy()
    book["mob_now"] = T - book["orig_month"] + 1
    book = book[(book["product"] == "revolving") | (book["mob_now"] < book["term_months"])]
    hz = km_hazards(km_by_grade, 120)
    open_def = D[~D["workout_closed"]]
    s3 = stage3_ecl(open_def, lgd)
    s3_down = stage3_ecl(open_def, lgd, "downturn_lgd")
    res, detail = {}, {}
    for name in SCENARIOS:
        key = "downturn_lgd" if name == "downside" else "lgd"
        e = compute_ecl(book, hz, P_by_product, lgd, ccf["ccf_mean"], rho, zs[name], lgd_key=key)
        res[name] = float(e["ecl"].sum()) + (s3_down if name == "downside" else s3)
        detail[name] = e
    weights = {k: v["weight"] for k, v in SCENARIOS.items()}
    ecl_w = weighted_ecl(res, weights)
    base = detail["base"]
    stage_tbl = base.groupby("stage").agg(n=("loan_id", "size"), ead=("ead_now", "sum"), ecl=("ecl", "sum")).reset_index()
    stage_tbl.loc[len(stage_tbl)] = [3, len(open_def), float(open_def["ead"].sum()), s3]
    stage_tbl["coverage"] = stage_tbl["ecl"] / stage_tbl["ead"]
    stage_tbl.to_csv(OUT / "ecl_by_stage_base.csv", index=False)
    print(f"[6/9] ECL base={res['base']:,.0f} up={res['upside']:,.0f} down={res['downside']:,.0f} → ponderada={ecl_w:,.0f}")

    # ---- 7. waterfall
    e1 = compute_ecl(book, hz, P_by_product, lgd, ccf["ccf_mean"], rho, None, use_pit=False, force_stage1=True)
    e2 = compute_ecl(book, hz, P_by_product, lgd, ccf["ccf_mean"], rho, None, use_pit=False)
    e3 = detail["base"]
    res_nodown = {n: (float(detail[n]["ecl"].sum()) if n != "downside" else
                      float(compute_ecl(book, hz, P_by_product, lgd, ccf["ccf_mean"], rho, zs["downside"])["ecl"].sum()))
                  for n in SCENARIOS}
    e4 = weighted_ecl(res_nodown, weights)
    steps = [("1. ECL 12m, todos em Stage 1, PD TTC (KM)", float(e1["ecl"].sum())),
             ("2. + staging (lifetime p/ Stage 2: SICR + 30 DPD)", float(e2["ecl"].sum())),
             ("3. + PIT no cenário base", float(e3["ecl"].sum())),
             ("4. + ponderação de cenários (50/20/30)", e4),
             ("5. + LGD downturn no cenário adverso", ecl_w - weights["base"] * s3 - weights["upside"] * s3
              - weights["downside"] * s3_down),
             ("6. + Stage 3 (workouts abertos)", ecl_w)]
    wf = pd.DataFrame(steps, columns=["step", "ecl"])
    wf["delta"] = wf["ecl"].diff().fillna(wf["ecl"])
    wf.to_csv(OUT / "ecl_waterfall.csv", index=False)
    fig, ax = plt.subplots(figsize=(9, 4.2))
    ax.bar(range(len(wf)), wf["delta"], bottom=wf["ecl"] - wf["delta"], color=["#2f5d8a"] + ["#d9822b"] * 5)
    ax.set_xticks(range(len(wf)), [s.split(".")[0] for s in wf["step"]])
    ax.set(title="Waterfall de drivers da ECL", ylabel="ECL")
    _fig("ecl_waterfall")
    simple_vs = {"stage2_ecl_survival": float(e2.loc[e2["stage"] == 2, "ecl"].sum())}

    # ---- 8. sensibilidade
    sens = []
    for wd in (0.2, 0.3, 0.4, 0.5):
        w = {"base": 0.8 - wd, "upside": 0.2, "downside": wd}
        sens.append({"parameter": "peso downside", "value": wd, "ecl_weighted": weighted_ecl(res, w)})
    for r_ in (0.08, 0.12, 0.20):
        zr = scenario_z(sat, r_)
        rr = {n: float(compute_ecl(book, hz, P_by_product, lgd, ccf["ccf_mean"], r_, zr[n],
                                   lgd_key="downturn_lgd" if n == "downside" else "lgd")["ecl"].sum())
              + (s3_down if n == "downside" else s3) for n in SCENARIOS}
        sens.append({"parameter": "rho (correlação de ativos)", "value": r_, "ecl_weighted": weighted_ecl(rr, weights)})
    sens_df = pd.DataFrame(sens)
    sens_df.to_csv(OUT / "sensitivity.csv", index=False)

    # ---- 9. validation pack
    disc = discrimination(obs12["def_12m"], obs12["pd_12m_at_origination"])
    obs12 = obs12.assign(pd_ttc_12m=obs12["pd_ttc"])
    calib = calibration_by_grade(obs12, "pd_12m_at_origination")
    vb = vintage_backtest(obs12, "pd_12m_at_origination")
    stab = grade_psi(L.loc[L["orig_month"] < 12, "grade"], L.loc[L["orig_month"] >= 12, "grade"])
    n_red = int((vb["traffic_light"] == "red").sum())
    n_miscal = int((calib["result"] != "ok").sum())
    pack = {
        "generated_at": datetime.now(timezone.utc).isoformat(),
        "inventory": [{"model": "PD lifetime (KM por rating + Markov p/ atraso)", "owner": "autor (portfólio)",
                       "tier": "alto (provisão)", "status": "validado tecnicamente — aprovação pendente",
                       "last_validation": datetime.now(timezone.utc).date().isoformat()},
                      {"model": "Satélite macro (probit DR ~ desemprego + PIB)", "owner": "autor", "tier": "alto",
                       "status": "exploratório — série curta (≤54 meses)", "last_validation": "idem"},
                      {"model": "LGD workout (garantia/LTV, downturn)", "owner": "autor", "tier": "médio",
                       "status": "validado tecnicamente — viés de resolução declarado", "last_validation": "idem"},
                      {"model": "CCF rotativo", "owner": "autor", "tier": "médio", "status": "validado tecnicamente",
                       "last_validation": "idem"}],
        "discrimination": disc, "calibration": calib, "stability": {"grade_mix_psi": stab},
        "vintage_backtest": vb, "benchmark": bench, "sensitivity": sens_df,
        "limitations": [
            "Painel 100% sintético: valida software e método, não uma carteira real.",
            "Série macro curta (54 meses, 1 recessão): satélite com poucos graus de liberdade.",
            "KM trata pré-pagamento como censura (PD 'na ausência de saída'); a incidência cumulativa com risco competitivo é reportada ao lado.",
            "Cauda da hazard além do MOB observado extrapolada pela média dos últimos 12 meses.",
            "Workouts abertos excluídos da LGD (viés de resolução).",
            "Vida comportamental do rotativo fixada em 36 meses (premissa).",
            "Sem calibração regulatória; cenários e pesos ilustrativos.",
        ],
        "conclusion": (f"Discriminação Gini={disc['gini']:.3f}. Calibração: {n_miscal} de {len(calib)} ratings fora do IC "
                       f"de Jeffreys. Backtesting por safra: {n_red} safra(s) em vermelho. "
                       "Status sugerido: **aprovado com ressalvas** para uso em PoC; requer revisão humana."),
    }
    (OUT / "validation_pack.md").write_text(render_markdown(pack), encoding="utf-8")

    summary = {
        "version": "2.1.0", "seed": seed, "elapsed_seconds": round(time.perf_counter() - t0, 1),
        "panel": {"n_loans": len(L), "n_rows": len(P), "n_defaults": len(D), "rho": rho},
        "survival": {"pd12_km": pd12_km, "weibull_shape": wb.shape, "cox": cox.summary().round(4).to_dict(orient="records"),
                     "benchmark": bench.round(5).to_dict(orient="records")},
        "roll_rates": roll_rates(Pm),
        "satellite": {k: v for k, v in sat.items() if k != "model"},
        "scenario_z": {k: v.tolist() for k, v in zs.items()},
        "lgd": {k: v for k, v in lgd.items() if k != "by_segment"}, "ccf": ccf,
        "ecl": {"by_scenario": res, "weights": weights, "weighted": ecl_w,
                "weighted_minus_base": ecl_w - res["base"], "stage3": s3,
                "by_stage_base": stage_tbl.round(4).to_dict(orient="records"),
                "book": {"n": int(len(book)), "n_open_workouts": int(len(open_def))}},
        "waterfall": wf.round(2).to_dict(orient="records"),
        "sensitivity": sens_df.round(2).to_dict(orient="records"),
        "validation": {"discrimination": disc, "calibration": calib.round(4).to_dict(orient="records"),
                       "grade_mix_psi": stab, "vintage_backtest": vb.round(4).to_dict(orient="records")},
        "bayesian_pd": bayes.round(5).to_dict(orient="records"),
        "stage2_detail": simple_vs,
        "audit_log": audit.to_list(),
    }
    (OUT / "summary.json").write_text(json.dumps(summary, indent=2, ensure_ascii=False, default=float), encoding="utf-8")
    print(f"[9/9] validation pack: Gini={disc['gini']:.3f}, calibração fora do IC={n_miscal}, safras vermelhas={n_red} "
          f"— {summary['elapsed_seconds']}s")
    return summary


if __name__ == "__main__":
    main()
