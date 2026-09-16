import numpy as np
import pandas as pd

from src.data.synthetic_portfolio import (
    generate_policyholders,
    build_monthly_exposure,
    simulate_claims,
)
from src.actuarial.experience_engine import ae_ratio_by_cell
from src.validation.diagnostics import internal_consistency_check


def _small_config():
    return dict(n=3000, start="2020-01-01", end="2024-12-01", seed=7)


def test_generate_policyholders_shape_and_domain():
    cfg = _small_config()
    df = generate_policyholders(cfg["n"], age_min=18, age_max=85, seed=cfg["seed"])
    assert len(df) == cfg["n"]
    assert set(df["sex"].unique()) <= {"male", "female"}
    assert df["entry_age"].between(18, 85).all()
    assert (df["benefit_reference"] > 0).all()


def test_build_monthly_exposure_no_duplicates_per_policy_month():
    cfg = _small_config()
    ph = generate_policyholders(cfg["n"], seed=cfg["seed"])
    exposure = build_monthly_exposure(ph, cfg["start"], cfg["end"], seed=cfg["seed"])
    dup = exposure.duplicated(subset=["policy_id", "year_month"]).sum()
    assert dup == 0, "não deve haver exposição duplicada para a mesma apólice no mesmo mês"


def test_simulate_claims_truncates_exposure_at_event():
    cfg = _small_config()
    ph = generate_policyholders(cfg["n"], seed=cfg["seed"])
    exposure_raw = build_monthly_exposure(ph, cfg["start"], cfg["end"], seed=cfg["seed"])
    kept_exposure, claims = simulate_claims(exposure_raw, seed=cfg["seed"])

    # cada apólice com sinistro não deve ter exposição registrada após o mês do evento
    claims_idx = claims.set_index("policy_id")["occurrence_month"]
    for policy_id, occ_month in claims_idx.items():
        policy_exposure = kept_exposure[kept_exposure["policy_id"] == policy_id]
        assert (policy_exposure["year_month"] <= occ_month).all()


def test_no_duplicate_claims_per_policy():
    cfg = _small_config()
    ph = generate_policyholders(cfg["n"], seed=cfg["seed"])
    exposure_raw = build_monthly_exposure(ph, cfg["start"], cfg["end"], seed=cfg["seed"])
    _, claims = simulate_claims(exposure_raw, seed=cfg["seed"])
    assert claims["policy_id"].is_unique, "cada apólice deve gerar no máximo um sinistro (truncamento correto)"


def test_dataset_internally_consistent_ae_near_100pct():
    """Verificação central: como os sinistros são gerados pela própria tábua
    base, o A/E agregado do peculio deve ficar próximo de 100% (dentro de
    tolerância estatística) — se não ficar, há um bug na geração ou na
    reconciliação."""
    cfg = dict(n=20000, start="2018-01-01", end="2025-12-01", seed=42)
    ph = generate_policyholders(cfg["n"], seed=cfg["seed"])
    exposure_raw = build_monthly_exposure(ph, cfg["start"], cfg["end"], seed=cfg["seed"])
    exposure, claims = simulate_claims(exposure_raw, seed=cfg["seed"])

    peculio_exp = exposure[exposure["product"] == "peculio"]
    peculio_claims = claims[claims["product"] == "peculio"]

    cell_df = ae_ratio_by_cell(peculio_exp, peculio_claims, include_status=("oficial", "sensibilidade"))
    total_obs = cell_df["observed_events"].sum()
    total_exp = cell_df["expected_events"].sum()

    result = internal_consistency_check(total_obs, total_exp, tolerance=0.30)
    assert result["within_tolerance"], result["interpretation"]
