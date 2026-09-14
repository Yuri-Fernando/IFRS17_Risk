"""Testes unitários — Credit Risk ECL Engine."""

import sys
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

from src.data.load_data import generate_synthetic_portfolio
from src.data.preprocess import prepare_dataset
from src.modeling.ead_model import estimate_ead
from src.modeling.ecl_calculation import calculate_ecl, portfolio_totals
from src.modeling.lgd_model import estimate_lgd
from src.modeling.pd_model import select_champion, train_gbm_pd, train_logistic_pd
from src.modeling.staging import apply_staging, classify_stage, lifetime_pd
from src.simulation.copula_simulation import simulate_portfolio_losses
from src.validation.backtesting import kupiec_pof_test
from src.validation.model_validation import psi


@pytest.fixture(scope="module")
def synthetic_df():
    return generate_synthetic_portfolio(n=500, seed=1)


@pytest.fixture(scope="module")
def prepared(synthetic_df):
    return prepare_dataset(synthetic_df)


def test_synthetic_portfolio_shape(synthetic_df):
    assert len(synthetic_df) == 500
    assert "default" in synthetic_df.columns
    assert synthetic_df["default"].isin([0, 1]).all()


def test_prepare_dataset_split(prepared):
    assert len(prepared.X_train) + len(prepared.X_test) == len(prepared.df_full)
    assert "segment" not in prepared.feature_columns
    assert "contract_id" not in prepared.feature_columns


def test_pd_models_train_and_score(prepared):
    logistic = train_logistic_pd(prepared.X_train, prepared.y_train, prepared.X_test, prepared.y_test)
    gbm = train_gbm_pd(prepared.X_train, prepared.y_train, prepared.X_test, prepared.y_test)

    assert 0 <= logistic.auc <= 1
    assert 0 <= gbm.auc <= 1
    assert (logistic.pd_test >= 0).all() and (logistic.pd_test <= 1).all()

    champion = select_champion([logistic, gbm])
    assert champion.model_name in {"logistic_regression", "gradient_boosting"}


def test_lifetime_pd_monotonic_with_term():
    pd_12m = np.array([0.05, 0.05])
    term = np.array([12, 60])
    lt_pd = lifetime_pd(pd_12m, term)
    assert lt_pd[1] > lt_pd[0]  # prazo maior => PD lifetime maior


def test_classify_stage_default_is_always_stage3():
    pd_current = np.array([0.02, 0.5])
    pd_origination = np.array([0.02, 0.02])
    is_default = np.array([0, 1])
    stage = classify_stage(pd_current, pd_origination, is_default)
    assert stage[1] == 3


def test_lgd_bounded_between_0_and_1(synthetic_df):
    lgd = estimate_lgd(synthetic_df)
    assert (lgd > 0).all() and (lgd < 1).all()


def test_ead_non_negative(synthetic_df):
    ead = estimate_ead(synthetic_df)
    assert (ead >= 0).all()


def test_ecl_pipeline_end_to_end(synthetic_df, prepared):
    from src.data.preprocess import assign_segment

    logistic = train_logistic_pd(prepared.X_train, prepared.y_train, prepared.X_test, prepared.y_test)
    from src.modeling.pd_model import score_full_portfolio

    pd_full = score_full_portfolio(logistic, prepared.df_full[prepared.feature_columns])
    staged = apply_staging(prepared.df_full, pd_full)

    lgd = estimate_lgd(staged)
    ead = estimate_ead(staged)
    df_ecl = calculate_ecl(staged, lgd, ead)

    totals = portfolio_totals(df_ecl)
    assert totals["total_ecl"] >= 0
    assert totals["total_ecl"] <= totals["total_exposure"]
    assert totals["n_stage1"] + totals["n_stage2"] + totals["n_stage3"] == totals["n_contracts"]


def test_copula_simulation_produces_valid_distribution(synthetic_df, prepared):
    from src.modeling.pd_model import score_full_portfolio

    logistic = train_logistic_pd(prepared.X_train, prepared.y_train, prepared.X_test, prepared.y_test)
    pd_full = score_full_portfolio(logistic, prepared.df_full[prepared.feature_columns])
    staged = apply_staging(prepared.df_full, pd_full)
    lgd = estimate_lgd(staged)
    ead = estimate_ead(staged)
    df_ecl = calculate_ecl(staged, lgd, ead)

    result = simulate_portfolio_losses(df_ecl, n_simulations=500)
    assert len(result.losses) == 500
    assert result.var["var_99.9"] >= result.var["var_95"]
    assert result.expected_loss >= 0


def test_psi_identical_distributions_is_near_zero():
    rng = np.random.default_rng(0)
    sample = rng.uniform(0, 1, size=1000)
    value = psi(sample, sample)
    assert value < 1e-6


def test_kupiec_test_accepts_matching_rate():
    result = kupiec_pof_test(n_observations=1000, n_defaults=50, pd_predicted=0.05)
    assert result["reject_h0"] is False
