"""
Executa o pipeline completo de Ajuste ao Risco (AR) via linha de comando,
sem depender do Jupyter — útil para CI, automação ou execução em lote.

Uso:
    python run_pipeline.py [--config config/config.yaml] [--output reports/results]
"""
from __future__ import annotations

import argparse
import json
import os

import yaml

from src.data.synthetic_portfolio import build_synthetic_dataset
from src.actuarial.experience_engine import ae_ratio_by_cell, monthly_loss_ratio_series
from src.actuarial.credibility import apply_credibility
from src.validation.diagnostics import internal_consistency_check, chi_square_ae_test
from src.modeling.distribution_fit import select_best_distribution
from src.simulation.monte_carlo import run_monte_carlo, estimate_zero_probability, convergence_test
from src.risk_adjustment.ar_engine import compute_component_ar, combine_components, solvency_ii_benchmark_check
from src.risk_adjustment.correlation import simulate_adverse_correlation_scenario
from src.governance.audit_trail import default_registry


def main(config_path: str, output_dir: str) -> dict:
    with open(config_path, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)

    os.makedirs(output_dir, exist_ok=True)

    print("[1/8] Gerando portfólio sintético...")
    dataset = build_synthetic_dataset(config)
    policyholders, exposure, claims = dataset["policyholders"], dataset["exposure"], dataset["claims"]
    print(f"      {len(policyholders):,} segurados | {len(exposure):,} linhas de exposição | {len(claims):,} sinistros")

    print("[2/8] Verificando consistência interna (A/E)...")
    peculio_exp = exposure[exposure["product"] == "peculio"]
    peculio_claims = claims[claims["product"] == "peculio"]
    cell_df = ae_ratio_by_cell(peculio_exp, peculio_claims, include_status=("oficial", "sensibilidade"))
    total_obs, total_exp = cell_df["observed_events"].sum(), cell_df["expected_events"].sum()
    consistency = internal_consistency_check(total_obs, total_exp, tolerance=0.30)
    print(f"      A/E={total_obs/total_exp:.1%} | {consistency['interpretation']}")

    print("[3/8] Ajustando distribuição estatística...")
    mlr = monthly_loss_ratio_series(peculio_exp, peculio_claims)
    best_dist, comparison = select_best_distribution(mlr["loss_ratio"].values, candidates=config["distribution_fit"]["candidates"])
    print(f"      Distribuição selecionada: {best_dist.distribution.upper()} (AIC={best_dist.aic:.2f})")

    print("[4/8] Rodando simulação de Monte Carlo...")
    p0 = estimate_zero_probability(mlr["loss_ratio"].values)
    mc_conf, rar_conf = config["monte_carlo"], config["risk_adjustment"]
    mc_result = run_monte_carlo(
        mlr["loss_ratio"].values, distribution=best_dist.distribution, n_scenarios=mc_conf["n_scenarios"],
        seed=config["seed"], zero_probability=p0, target_percentiles=tuple(rar_conf["target_percentiles"]),
    )
    default_p = rar_conf["default_percentile"]
    stress_factor = mc_result.stress_factor(default_p)
    print(f"      Fator de stress (P{default_p}): {stress_factor:.4f}")

    print("[5/8] Testando convergência do número de cenários...")
    records, converged = convergence_test(
        mlr["loss_ratio"].values, best_dist.distribution, mc_conf["convergence_check_sizes"], default_p,
        seed=config["seed"], tolerance=mc_conf["convergence_tolerance"],
    )
    print(f"      Convergiu: {converged}")

    print("[6/8] Calculando AR por componente (BEL base vs. estressado)...")
    discount_rate = config["mortality"]["discount_rate_annual"]
    components = ["peculio", "pensao_por_morte", "renda_invalidez", "pensao_menor", "previdencia_longevidade"]
    component_results = {p: compute_component_ar(p, policyholders, stress_factor, default_p, discount_rate) for p in components}
    combined = combine_components(list(component_results.values()), diversification_benefit=rar_conf["diversification_benefit"])
    print(f"      AR diversificado total: R$ {combined['ar_diversified']:,.0f} ({combined['ar_diversified_pct_of_bel']:.2%} do BEL)")

    print("[7/8] Simulando cenário de correlação adversa...")
    adverse = simulate_adverse_correlation_scenario(
        n_scenarios=mc_conf["n_scenarios"], corr_longevity_conversion=rar_conf["adverse_correlation"]["longevity_conversion"],
        corr_longevity_lapse=rar_conf["adverse_correlation"]["longevity_lapse"], target_percentile=default_p, seed=config["seed"],
    )

    print("[8/8] Exportando resultados e registro de premissas...")
    sii_check = solvency_ii_benchmark_check(stress_factor, default_p, config["solvency_ii_benchmark"]["mortality_shock"])
    chi2 = chi_square_ae_test(total_obs, total_exp, n_cells=cell_df["age_band"].nunique())

    final_results = {
        "config": config,
        "dataset_summary": {"n_policyholders": len(policyholders), "n_exposure_rows": len(exposure), "n_claims": len(claims)},
        "ae_ratio_peculio": float(total_obs / total_exp),
        "chi_square_test": chi2,
        "distribution_selected": best_dist.distribution,
        "monte_carlo": {
            "p0": float(p0), "median_simulated": mc_result.median_simulated, "percentiles": mc_result.percentiles,
            "stress_factors": {str(p): mc_result.stress_factor(p) for p in rar_conf["target_percentiles"]},
            "convergence_records": records, "converged": converged,
        },
        "solvency_ii_benchmark": sii_check,
        "components": {p: {"bel_base": r.bel_base, "bel_stress": r.bel_stress, "ar_monetary": r.ar_monetary, "ar_pct_of_bel": r.ar_pct_of_bel} for p, r in component_results.items()},
        "combined": combined,
        "adverse_correlation_scenario": adverse.summary(),
    }

    with open(os.path.join(output_dir, "final_results.json"), "w", encoding="utf-8") as f:
        json.dump(final_results, f, indent=2, default=str, ensure_ascii=False)

    registry = default_registry(config)
    with open("reports/assumptions.md", "w", encoding="utf-8") as f:
        f.write("# Registro de Premissas — pension-risk-adjustment-engine\n\n")
        f.write(registry.to_markdown())

    print(f"\nConcluído. Resultados em {output_dir}/final_results.json")
    return final_results


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Executa o pipeline de Ajuste ao Risco de ponta a ponta.")
    parser.add_argument("--config", default="config/config.yaml")
    parser.add_argument("--output", default="reports/results")
    args = parser.parse_args()
    main(args.config, args.output)
