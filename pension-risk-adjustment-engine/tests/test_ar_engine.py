import pandas as pd

from src.risk_adjustment.ar_engine import (
    compute_component_ar,
    combine_components,
    solvency_ii_benchmark_check,
)


def _sample_policyholders():
    return pd.DataFrame(
        {
            "policy_id": [1, 2, 3, 4],
            "sex": ["male", "female", "male", "female"],
            "entry_age": [45, 50, 55, 60],
            "product": ["peculio", "peculio", "peculio", "peculio"],
            "benefit_reference": [200000, 250000, 300000, 150000],
        }
    )


def test_stress_factor_one_gives_zero_ar():
    ph = _sample_policyholders()
    result = compute_component_ar("peculio", ph, stress_factor=1.0, target_percentile=80, discount_rate=0.06)
    assert abs(result.ar_monetary) < 1e-6, "fator de stress 1.0 não deve gerar nenhum AR"


def test_higher_stress_gives_higher_ar_for_mortality_product():
    ph = _sample_policyholders()
    low = compute_component_ar("peculio", ph, stress_factor=1.05, target_percentile=80, discount_rate=0.06)
    high = compute_component_ar("peculio", ph, stress_factor=1.20, target_percentile=80, discount_rate=0.06)
    assert high.ar_monetary > low.ar_monetary > 0


def test_longevity_stress_direction_increases_bel_when_qx_falls():
    ph = _sample_policyholders().assign(product="previdencia_longevidade")
    result = compute_component_ar("previdencia_longevidade", ph, stress_factor=1.10, target_percentile=80, discount_rate=0.06)
    # direção -1: fator > 1 reduz o QX (mais longevidade) -> BEL_stress > BEL_base -> AR > 0
    assert result.ar_monetary > 0


def test_combine_components_applies_diversification():
    ph = _sample_policyholders()
    c1 = compute_component_ar("peculio", ph, stress_factor=1.10, target_percentile=80, discount_rate=0.06)
    combined = combine_components([c1, c1], diversification_benefit=0.20)
    expected_sum = c1.ar_monetary * 2
    assert combined["ar_sum_simple"] == expected_sum
    assert combined["ar_diversified"] == expected_sum * 0.80


def test_solvency_ii_benchmark_consistent_for_lower_percentile():
    check = solvency_ii_benchmark_check(stress_factor=1.05, target_percentile=80, sii_shock=0.15)
    assert check["directionally_consistent"] is True


def test_solvency_ii_benchmark_flags_inconsistency():
    check = solvency_ii_benchmark_check(stress_factor=1.50, target_percentile=80, sii_shock=0.15)
    assert check["directionally_consistent"] is False
