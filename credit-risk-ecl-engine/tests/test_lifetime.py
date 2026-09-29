"""Testes da extensão lifetime/forward-looking (v2.1)."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest
from scipy import integrate
from scipy.stats import norm

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.panel import generate_loan_panel, mob_shape  # noqa: E402
from src.modeling.bayesian_pd import beta_binomial_pd  # noqa: E402
from src.modeling.lgd_ead_advanced import amortizing_balance, estimate_ccf, workout_lgd  # noqa: E402
from src.modeling.lifetime_ecl import marginal_from_hazard, pit_adjust_monthly, weighted_ecl  # noqa: E402
from src.modeling.macro_pit import vasicek_pit  # noqa: E402
from src.modeling.survival.survival_models import (fit_cox, fit_weibull_aft, kaplan_meier,  # noqa: E402
                                                   simple_lifetime_pd, term_structure)
from src.modeling.vintage_migration import markov_lifetime_pd, transition_matrix  # noqa: E402


@pytest.fixture(scope="module")
def panel():
    return generate_loan_panel(n_loans=1500, n_cohorts=20, n_months=40, seed=7)


def test_kaplan_meier_manual_example():
    # tempos 1,2,2,3,4 ; eventos 1,1,0,1,0 → S(1)=4/5, S(2)=4/5·3/4, S(3)=·1/2
    km = kaplan_meier([1, 2, 2, 3, 4], [1, 1, 0, 1, 0], 4).set_index("t")
    assert km.loc[1, "survival"] == pytest.approx(0.8)
    assert km.loc[2, "survival"] == pytest.approx(0.6)
    assert km.loc[3, "survival"] == pytest.approx(0.3)
    assert km.loc[4, "survival"] == pytest.approx(0.3)


def test_weibull_recovers_parameters():
    rng = np.random.default_rng(1)
    n, k, lam = 4000, 1.5, 40.0
    t = lam * rng.weibull(k, n)
    c = rng.uniform(10, 80, n)
    dur, ev = np.ceil(np.minimum(t, c)), (t <= c).astype(int)
    m = fit_weibull_aft(pd.DataFrame(index=range(n)), dur, ev)
    assert m.shape == pytest.approx(k, rel=0.08)
    assert np.exp(m.beta[0]) == pytest.approx(lam, rel=0.08)


def test_cox_recovers_hazard_ratio():
    rng = np.random.default_rng(2)
    n = 3000
    x = rng.integers(0, 2, n).astype(float)
    t = rng.exponential(1 / (0.02 * np.exp(0.8 * x)))
    c = rng.uniform(5, 100, n)
    m = fit_cox(pd.DataFrame({"x": x}), np.ceil(np.minimum(t, c)), (t <= c).astype(int))
    assert m.params[0] == pytest.approx(0.8, abs=0.12)
    S = m.survival(pd.DataFrame({"x": [0.0, 1.0]}), np.array([12.0]))
    assert S[1, 0] < S[0, 0]


def test_term_structure_and_simple_formula():
    cum = 1 - np.cumprod(np.full(48, 1 - 0.01))
    ts = term_structure(cum, 4)
    np.testing.assert_allclose(ts["marginal_pd"].sum(), ts["cumulative_pd"].iloc[-1])
    # hazard constante ⇒ fórmula simples é exata
    assert ts["cumulative_pd"].iloc[2] == pytest.approx(simple_lifetime_pd(ts["cumulative_pd"].iloc[0], 36))


def test_vasicek_pit_integrates_to_ttc():
    ttc, rho = 0.05, 0.12
    mean, _ = integrate.quad(lambda z: vasicek_pit(ttc, z, rho) * norm.pdf(z), -8, 8)
    assert mean == pytest.approx(ttc, rel=1e-6)
    assert vasicek_pit(ttc, -2.0, rho) > ttc > vasicek_pit(ttc, 2.0, rho)


def test_pit_adjust_and_marginals():
    h = np.full(24, 0.004)
    assert np.all(pit_adjust_monthly(h, np.array([-2.0, -2.0]), 0.12) > h)
    q = marginal_from_hazard(h)
    assert q.sum() == pytest.approx(1 - (1 - 0.004) ** 24)


def test_weighted_ecl_convexity():
    """Com fator adverso mais forte que o favorável, E[ECL] > ECL(base) — não-linearidade."""
    ecl = {s: float(vasicek_pit(0.03, z, 0.12)) for s, z in {"base": 0.0, "up": 1.0, "down": -1.0}.items()}
    assert weighted_ecl(ecl, {"base": 0.5, "up": 0.25, "down": 0.25}) > ecl["base"]


def test_transition_matrix_properties(panel):
    P = transition_matrix(panel.panel)
    np.testing.assert_allclose(P.sum(axis=1).to_numpy(), 1.0, atol=1e-9)
    assert P.loc["DEF", "DEF"] == 1.0
    life = markov_lifetime_pd(P, 36)
    assert np.all(np.diff(life) >= -1e-12)
    assert markov_lifetime_pd(P, 12, "D60")[-1] > markov_lifetime_pd(P, 12, "C")[-1]


def test_panel_invariants(panel):
    L, D = panel.loans, panel.defaults
    assert (L["duration_months"] >= 1).all()
    assert set(L.loc[L["event_default"] == 1, "loan_id"]) == set(D["loan_id"])
    assert D["realized_lgd"].between(0, 1).all()
    assert (D.loc[D["secured"], "realized_lgd"].mean() < D.loc[~D["secured"], "realized_lgd"].mean())
    assert abs(mob_shape(np.arange(1, 49)).mean() - 1.0) < 0.05


def test_workout_lgd_and_amortization():
    assert workout_lgd(1000, [600], [12], [0], 0.0) == pytest.approx(0.4)
    lgd = workout_lgd(1000, [600], [12], [0], 0.10)
    assert lgd == pytest.approx(1 - 0.6 / 1.10, rel=1e-6)
    assert amortizing_balance(1000, 0.12, 12, 0) == pytest.approx(1000)
    assert amortizing_balance(1000, 0.12, 12, 12) == pytest.approx(0.0)
    assert 0 < amortizing_balance(1000, 0.12, 12, 6) < 1000


def test_ccf_definition():
    d = pd.DataFrame({"product": ["revolving"] * 2, "limit": [1000.0, 1000.0], "drawn_12m_before": [200.0, 500.0],
                      "ead": [600.0, 500.0]})
    r = estimate_ccf(d)
    assert r["ccf_mean"] == pytest.approx((0.5 + 0.0) / 2)


def test_bayesian_shrinkage():
    df = pd.DataFrame({"seg": ["grande", "pequeno", "medio"], "n": [5000, 20, 800], "defaults": [250, 5, 40]})
    r = beta_binomial_pd(df, "seg").set_index("seg")
    prior_mean = r["prior_alpha"].iloc[0] / (r["prior_alpha"].iloc[0] + r["prior_beta"].iloc[0])
    small = r.loc["pequeno"]
    assert min(prior_mean, small["raw_pd"]) <= small["posterior_mean"] <= max(prior_mean, small["raw_pd"])
    assert r.loc["grande", "credibility_Z"] > r.loc["pequeno", "credibility_Z"]
    assert (r["ci_low"] <= r["posterior_mean"]).all() and (r["posterior_mean"] <= r["ci_high"]).all()
