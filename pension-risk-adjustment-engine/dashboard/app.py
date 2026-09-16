"""
Dashboard interativo — Motor de Ajuste ao Risco (AR) para Previdência Multi-Produto.

Rodar com:
    streamlit run dashboard/app.py

Consome os resultados gerados pelo notebook (reports/results/final_results.json)
como visão estática de referência, e permite recalcular interativamente o AR
para diferentes percentis-alvo e benefícios de diversificação, usando os
mesmos módulos do pacote `src` — nenhuma duplicação de lógica.
"""
import json
import os
import sys

import pandas as pd
import streamlit as st
import yaml

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from src.data.synthetic_portfolio import build_synthetic_dataset
from src.actuarial.experience_engine import ae_ratio_by_cell, monthly_loss_ratio_series
from src.modeling.distribution_fit import select_best_distribution
from src.simulation.monte_carlo import run_monte_carlo, estimate_zero_probability
from src.risk_adjustment.ar_engine import compute_component_ar, combine_components, solvency_ii_benchmark_check, STRESS_DIRECTION
from src.risk_adjustment.correlation import simulate_adverse_correlation_scenario

st.set_page_config(page_title="AR Previdência — IFRS 17", page_icon="📐", layout="wide")

CONFIG_PATH = os.path.join(os.path.dirname(__file__), "..", "config", "config.yaml")
RESULTS_PATH = os.path.join(os.path.dirname(__file__), "..", "reports", "results", "final_results.json")


@st.cache_data(show_spinner="Gerando portfólio sintético e calculando pipeline...")
def load_pipeline(n_policyholders: int, seed: int, default_percentile: int):
    with open(CONFIG_PATH, "r", encoding="utf-8") as f:
        config = yaml.safe_load(f)
    config["portfolio"]["n_policyholders"] = n_policyholders
    config["seed"] = seed

    dataset = build_synthetic_dataset(config)
    policyholders, exposure, claims = dataset["policyholders"], dataset["exposure"], dataset["claims"]

    peculio_exp = exposure[exposure["product"] == "peculio"]
    peculio_claims = claims[claims["product"] == "peculio"]
    mlr = monthly_loss_ratio_series(peculio_exp, peculio_claims)

    cell_df = ae_ratio_by_cell(peculio_exp, peculio_claims, include_status=("oficial", "sensibilidade"))
    ae_ratio = cell_df["observed_events"].sum() / cell_df["expected_events"].sum()

    best_dist, comparison = select_best_distribution(mlr["loss_ratio"].values, candidates=["gamma", "lognorm", "norm"])
    p0 = estimate_zero_probability(mlr["loss_ratio"].values)

    mc_result = run_monte_carlo(
        mlr["loss_ratio"].values,
        distribution=best_dist.distribution,
        n_scenarios=config["monte_carlo"]["n_scenarios"],
        seed=seed,
        zero_probability=p0,
        target_percentiles=(75, 80, 90, default_percentile),
    )

    return {
        "config": config,
        "policyholders": policyholders,
        "ae_ratio": ae_ratio,
        "best_dist": best_dist,
        "comparison": comparison,
        "mc_result": mc_result,
        "mlr": mlr,
    }


st.title("📐 Motor de Ajuste ao Risco (AR) — Previdência Multi-Produto | IFRS 17")
st.caption(
    "v3 do repositório de portfólio IFRS17_Risk. Dados 100% sintéticos — "
    "metodologia consolidada a partir de itau/METODOLOGIA_MESTRE.md."
)

with st.sidebar:
    st.header("Parâmetros")
    n_policyholders = st.slider("Tamanho do portfólio sintético", 5_000, 100_000, 30_000, step=5_000)
    seed = st.number_input("Semente (reprodutibilidade)", value=42, step=1)
    target_percentile = st.select_slider("Percentil-alvo do AR", options=[75, 80, 90], value=80)
    diversification_benefit = st.slider("Benefício de diversificação entre caixinhas", 0.0, 0.40, 0.15, step=0.05)
    st.divider()
    st.markdown(
        "**Sobre os dados:** portfólio e sinistros são gerados por simulação a partir de "
        "tábuas biométricas paramétricas — nenhum número real de nenhuma carteira é usado. "
        "Ver `itau/METODOLOGIA_MESTRE.md` para a metodologia completa."
    )

pipeline = load_pipeline(n_policyholders, seed, target_percentile)
config = pipeline["config"]
mc_result = pipeline["mc_result"]
policyholders = pipeline["policyholders"]

tab1, tab2, tab3, tab4 = st.tabs(["📊 Visão Geral", "🎲 Monte Carlo", "🧩 AR por Componente", "🔗 Correlação Adversa"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    col1.metric("Segurados (sintético)", f"{len(policyholders):,}")
    col2.metric("A/E Ratio (Peculio)", f"{pipeline['ae_ratio']:.1%}")
    col3.metric("Distribuição selecionada", pipeline["best_dist"].distribution.upper())
    col4.metric("Fator de stress (alvo)", f"{mc_result.stress_factor(target_percentile):.4f}")

    st.subheader("Composição do portfólio sintético")
    st.bar_chart(policyholders["product"].value_counts())

    st.subheader("Comparação de distribuições (AIC/BIC/KS)")
    st.dataframe(pipeline["comparison"], use_container_width=True)

with tab2:
    st.subheader("Distribuição empírica simulada (Monte Carlo)")
    st.line_chart(pd.Series(mc_result.simulated_means).sort_values().reset_index(drop=True))

    col1, col2, col3 = st.columns(3)
    col1.metric("Mediana simulada (P50)", f"{mc_result.median_simulated:.4f}")
    col2.metric(f"P{target_percentile}", f"{mc_result.percentiles[target_percentile]:.4f}")
    col3.metric(f"CTE(P{target_percentile})", f"{mc_result.cte(target_percentile):.4f}")

    st.subheader("Sensibilidade do fator de stress ao percentil")
    sens = pd.DataFrame(
        {"percentil": [75, 80, 90], "fator_stress": [mc_result.stress_factor(p) for p in [75, 80, 90]]}
    )
    st.bar_chart(sens.set_index("percentil"))

    sii = solvency_ii_benchmark_check(mc_result.stress_factor(target_percentile), target_percentile, config["solvency_ii_benchmark"]["mortality_shock"])
    if sii["directionally_consistent"]:
        st.success(sii["interpretation"])
    else:
        st.warning(sii["interpretation"])

with tab3:
    st.subheader(f"AR por componente ('caixinha') — Percentil P{target_percentile}")
    discount_rate = config["mortality"]["discount_rate_annual"]
    stress_factor = mc_result.stress_factor(target_percentile)

    components = ["peculio", "pensao_por_morte", "renda_invalidez", "pensao_menor", "previdencia_longevidade"]
    rows = []
    results = []
    for p in components:
        r = compute_component_ar(p, policyholders, stress_factor, target_percentile, discount_rate)
        results.append(r)
        rows.append(
            {
                "produto": p,
                "direção": "mortalidade ↑" if STRESS_DIRECTION[p] > 0 else "longevidade (QX ↓)",
                "BEL_base": r.bel_base,
                "BEL_stress": r.bel_stress,
                "AR": r.ar_monetary,
                "AR_%_BEL": r.ar_pct_of_bel,
            }
        )
    df = pd.DataFrame(rows)
    st.dataframe(df.style.format({"BEL_base": "R$ {:,.0f}", "BEL_stress": "R$ {:,.0f}", "AR": "R$ {:,.0f}", "AR_%_BEL": "{:.2%}"}), use_container_width=True)
    st.bar_chart(df.set_index("produto")["AR_%_BEL"])

    combined = combine_components(results, diversification_benefit=diversification_benefit)
    col1, col2, col3 = st.columns(3)
    col1.metric("AR — soma simples", f"R$ {combined['ar_sum_simple']:,.0f}")
    col2.metric("AR — diversificado", f"R$ {combined['ar_diversified']:,.0f}")
    col3.metric("Impacto no CSM", f"-R$ {combined['csm_reduction']:,.0f}")
    st.info(
        f"Cada R$1 de AR reduz o CSM em R$1 (relação estrutural do IFRS 17: "
        f"CSM = Prêmio − BEL − AR). O AR diversificado representa "
        f"{combined['ar_diversified_pct_of_bel']:.2%} do BEL total dos componentes calculados."
    )

with tab4:
    st.subheader("Cenário de correlação adversa (Longevidade + Conversão + Resgate)")
    st.caption(
        "O pior cenário para produtos de renda vitalícia não é estressar cada premissa isoladamente, "
        "mas a combinação: mortalidade caindo, conversão subindo e resgate caindo simultaneamente."
    )
    adverse = simulate_adverse_correlation_scenario(
        n_scenarios=config["monte_carlo"]["n_scenarios"],
        corr_longevity_conversion=config["risk_adjustment"]["adverse_correlation"]["longevity_conversion"],
        corr_longevity_lapse=config["risk_adjustment"]["adverse_correlation"]["longevity_lapse"],
        target_percentile=target_percentile,
        seed=seed,
    )
    summary = adverse.summary()
    col1, col2, col3 = st.columns(3)
    col1.metric(f"Longevidade (P{target_percentile})", f"{summary['longevity_shift_pXX']:.3f}", help="< 1.0 = mais longevidade")
    col2.metric(f"Conversão (P{target_percentile})", f"{summary['conversion_shift_pXX']:.3f}")
    col3.metric(f"Resgate (P{target_percentile})", f"{summary['lapse_shift_pXX']:.3f}", help="< 1.0 = menos resgates (mais adverso)")

    chart_df = pd.DataFrame(
        {
            "longevidade": adverse.longevity_shift,
            "conversão": adverse.conversion_shift,
            "resgate": adverse.lapse_shift,
        }
    )
    st.line_chart(chart_df.sample(min(2000, len(chart_df))).reset_index(drop=True))

st.divider()
st.caption(
    "Este dashboard implementa a metodologia documentada em itau/METODOLOGIA_MESTRE.md com dados "
    "100% sintéticos. Não substitui modelos atuariais de produção nem processos de validação institucional."
)
