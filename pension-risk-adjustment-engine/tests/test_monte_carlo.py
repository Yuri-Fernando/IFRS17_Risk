import numpy as np

from src.simulation.monte_carlo import run_monte_carlo, convergence_test, estimate_zero_probability


def _synthetic_loss_ratio_series(seed=1, n=60):
    rng = np.random.default_rng(seed)
    zeros = rng.random(n) < 0.05
    values = rng.gamma(shape=4.0, scale=0.03, size=n)
    values[zeros] = 0.0
    return values


def test_reproducibility_same_seed_same_result():
    series = _synthetic_loss_ratio_series()
    r1 = run_monte_carlo(series, distribution="gamma", n_scenarios=2000, seed=42)
    r2 = run_monte_carlo(series, distribution="gamma", n_scenarios=2000, seed=42)
    assert r1.median_simulated == r2.median_simulated
    assert r1.percentiles == r2.percentiles


def test_different_seed_gives_different_result():
    series = _synthetic_loss_ratio_series()
    r1 = run_monte_carlo(series, distribution="gamma", n_scenarios=2000, seed=1)
    r2 = run_monte_carlo(series, distribution="gamma", n_scenarios=2000, seed=2)
    assert r1.median_simulated != r2.median_simulated


def test_stress_factor_greater_than_one_for_upper_percentile():
    series = _synthetic_loss_ratio_series()
    result = run_monte_carlo(series, distribution="gamma", n_scenarios=5000, seed=42, target_percentiles=(80,))
    assert result.stress_factor(80) > 1.0, "P80 deve ser maior que a mediana (P50) por definição"


def test_cte_greater_than_or_equal_var():
    series = _synthetic_loss_ratio_series()
    result = run_monte_carlo(series, distribution="gamma", n_scenarios=5000, seed=42, target_percentiles=(80,))
    var_80 = result.percentiles[80]
    cte_80 = result.cte(80)
    assert cte_80 >= var_80, "CTE (média da cauda) deve ser >= VaR/percentil por construção"


def test_convergence_detects_stability():
    series = _synthetic_loss_ratio_series(n=60)
    records, converged = convergence_test(series, "gamma", [1000, 5000, 10000, 30000], target_percentile=80)
    assert len(records) == 4
    assert isinstance(converged, bool)


def test_estimate_zero_probability():
    series = np.array([0.0, 0.1, 0.2, 0.0, 0.3])
    assert estimate_zero_probability(series) == 0.4
