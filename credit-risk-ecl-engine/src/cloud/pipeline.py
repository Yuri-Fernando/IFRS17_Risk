"""
Orquestração do pipeline completo — Credit Risk ECL Engine.

Fluxo:
1. Carga de dados (real German Credit ou sintético)
2. Pré-processamento e segmentação
3. Modelagem de PD (champion vs. challenger)
4. Staging IFRS 9 (SICR) + PD lifetime
5. Modelagem de LGD e EAD
6. Cálculo de ECL contábil (Stage 1/2/3)
7. Simulação de Monte Carlo com cópula (correlação entre segmentos) → VaR/CVaR
8. Validação (Gini, KS, PSI, calibração, backtesting Kupiec)
9. Stress testing
10. Trilha de auditoria e versionamento do modelo
"""

from __future__ import annotations

import time

import numpy as np

from src.data.load_data import load_portfolio
from src.data.preprocess import prepare_dataset
from src.governance.audit_log import AuditLog
from src.governance.model_versioning import ModelVersion
from src.modeling.ead_model import estimate_ead
from src.modeling.ecl_calculation import calculate_ecl, portfolio_totals, summarize_ecl_by_segment, summarize_ecl_by_stage
from src.modeling.lgd_model import estimate_lgd
from src.modeling.pd_model import score_full_portfolio, select_champion, train_gbm_pd, train_logistic_pd
from src.modeling.staging import apply_staging
from src.simulation.copula_simulation import simulate_portfolio_losses
from src.validation.backtesting import backtest_by_stage
from src.validation.model_validation import calibration_table, psi, psi_rating
from src.validation.stress_test import run_all_scenarios


def run_pipeline(
    data_source: str = "csv",
    data_path: str | None = None,
    n_simulations: int = 10000,
    inter_segment_correlation: float = 0.25,
    asset_correlation: float = 0.15,
    verbose: bool = True,
) -> dict:
    audit = AuditLog()
    t0 = time.time()

    # 1. Dados
    df = load_portfolio(source=data_source, path=data_path)
    audit.log("load_data", source=data_source, n_records=len(df))
    if verbose:
        print(f"[1/9] Dados carregados: {len(df)} contratos (fonte: {data_source})")

    # 2. Pré-processamento
    prepared = prepare_dataset(df)
    audit.log("preprocess", n_features=len(prepared.feature_columns))
    if verbose:
        print(f"[2/9] Pré-processamento: {len(prepared.feature_columns)} atributos, "
              f"split {len(prepared.X_train)}/{len(prepared.X_test)} (treino/teste)")

    # 3. Modelagem de PD — champion vs. challenger
    logistic_result = train_logistic_pd(prepared.X_train, prepared.y_train, prepared.X_test, prepared.y_test)
    gbm_result = train_gbm_pd(prepared.X_train, prepared.y_train, prepared.X_test, prepared.y_test)
    champion = select_champion([logistic_result, gbm_result])
    audit.log(
        "train_pd_models",
        logistic={"gini": logistic_result.gini, "ks": logistic_result.ks, "auc": logistic_result.auc},
        gbm={"gini": gbm_result.gini, "ks": gbm_result.ks, "auc": gbm_result.auc},
        champion=champion.model_name,
    )
    if verbose:
        print(f"[3/9] PD — Logistic Gini={logistic_result.gini:.3f} | GBM Gini={gbm_result.gini:.3f} "
              f"→ champion: {champion.model_name}")

    pd_12m_full = score_full_portfolio(champion, prepared.df_full[prepared.feature_columns])

    # 4. Staging IFRS 9
    df_staged = apply_staging(prepared.df_full, pd_12m_full)
    audit.log(
        "staging",
        n_stage1=int((df_staged["stage"] == 1).sum()),
        n_stage2=int((df_staged["stage"] == 2).sum()),
        n_stage3=int((df_staged["stage"] == 3).sum()),
    )
    if verbose:
        vc = df_staged["stage"].value_counts().sort_index()
        print(f"[4/9] Staging IFRS 9 — Stage1={vc.get(1,0)} Stage2={vc.get(2,0)} Stage3={vc.get(3,0)}")

    # 5. LGD e EAD
    lgd = estimate_lgd(df_staged)
    ead = estimate_ead(df_staged)
    audit.log("lgd_ead", avg_lgd=float(lgd.mean()), total_ead=float(ead.sum()))
    if verbose:
        print(f"[5/9] LGD médio={lgd.mean():.1%} | EAD total=R$ {ead.sum():,.2f}")

    # 6. ECL
    df_ecl = calculate_ecl(df_staged, lgd, ead)
    totals = portfolio_totals(df_ecl)
    by_stage = summarize_ecl_by_stage(df_ecl)
    by_segment = summarize_ecl_by_segment(df_ecl)
    audit.log("ecl_calculation", **totals)
    if verbose:
        print(f"[6/9] ECL total=R$ {totals['total_ecl']:,.2f} | Coverage ratio={totals['coverage_ratio']:.2%}")

    # 7. Simulação com cópula (correlação de risco entre segmentos)
    sim_result = simulate_portfolio_losses(
        df_ecl,
        n_simulations=n_simulations,
        inter_segment_correlation=inter_segment_correlation,
        asset_correlation=asset_correlation,
    )
    audit.log(
        "monte_carlo_copula",
        n_simulations=n_simulations,
        inter_segment_correlation=inter_segment_correlation,
        asset_correlation=asset_correlation,
        expected_loss=sim_result.expected_loss,
        var=sim_result.var,
        cvar=sim_result.cvar,
        diversification_benefit=sim_result.diversification_benefit,
    )
    if verbose:
        print(f"[7/9] Monte Carlo c/ cópula ({n_simulations} cenários) — "
              f"EL={sim_result.expected_loss:,.2f} | VaR99.9={sim_result.var.get('var_99.9', 0):,.2f} | "
              f"Benefício diversificação={sim_result.diversification_benefit:,.2f}")

    # 8. Validação
    psi_value = psi(logistic_result.pd_train, logistic_result.pd_test)
    calib_table = calibration_table(champion.pd_test, prepared.y_test.values)
    backtest_results = backtest_by_stage(df_ecl)
    audit.log(
        "validation",
        champion_gini=champion.gini,
        champion_ks=champion.ks,
        psi=psi_value,
        psi_rating=psi_rating(psi_value),
        backtest=backtest_results,
    )
    if verbose:
        print(f"[8/9] Validação — Gini={champion.gini:.3f} KS={champion.ks:.3f} PSI={psi_value:.4f} "
              f"({psi_rating(psi_value)})")

    # 9. Stress testing
    stress_results = run_all_scenarios(df_ecl)
    audit.log("stress_test", scenarios=stress_results.to_dict(orient="records"))
    if verbose:
        print("[9/9] Stress test concluído (4 cenários)")

    version = ModelVersion(
        model_name=champion.model_name,
        parameters={
            "n_simulations": n_simulations,
            "inter_segment_correlation": inter_segment_correlation,
            "asset_correlation": asset_correlation,
            "data_source": data_source,
        },
        gini=champion.gini,
        ks=champion.ks,
    )

    elapsed = time.time() - t0
    audit.log("pipeline_complete", elapsed_seconds=round(elapsed, 2))

    return {
        "status": "SUCCESS",
        "model_version": version.to_dict(),
        "pd_models": {
            "logistic_regression": {"gini": logistic_result.gini, "ks": logistic_result.ks, "auc": logistic_result.auc},
            "gradient_boosting": {"gini": gbm_result.gini, "ks": gbm_result.ks, "auc": gbm_result.auc},
            "champion": champion.model_name,
        },
        "portfolio": totals,
        "ecl_by_stage": by_stage.to_dict(orient="records"),
        "ecl_by_segment": by_segment.to_dict(orient="records"),
        "monte_carlo": {
            "n_simulations": n_simulations,
            "expected_loss": sim_result.expected_loss,
            "var": sim_result.var,
            "cvar": sim_result.cvar,
            "diversification_benefit": sim_result.diversification_benefit,
            "correlation_matrix": sim_result.correlation_matrix.to_dict(),
        },
        "validation": {
            "gini": champion.gini,
            "ks": champion.ks,
            "psi": psi_value,
            "psi_rating": psi_rating(psi_value),
            "calibration_table": calib_table.to_dict(orient="records"),
            "backtesting": backtest_results,
        },
        "stress_test": stress_results.to_dict(orient="records"),
        "audit_log": audit.to_list(),
        "elapsed_seconds": round(elapsed, 2),
        "df_ecl": df_ecl,  # mantido em memória para uso em notebook/CLI; removido antes de export JSON
    }
