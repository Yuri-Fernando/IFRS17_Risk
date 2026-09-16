"""
Gerador de portfólio sintético multi-produto de previdência/benefícios de risco.

Objetivo: reproduzir a ESTRUTURA de dados real descrita na metodologia (ver
itau/METODOLOGIA_MESTRE.md) — base de expostos (carteira ativa) + base de
sinistros/concedidos, relacionadas por idade x sexo x produto x mês — sem usar
nenhum número ou volume da carteira real de nenhuma instituição. Os sinistros
são gerados por sorteio de Bernoulli usando a própria tábua de mortalidade
paramétrica (src/data/mortality_tables.py), portanto o dataset é internamente
consistente e auditável, mas 100% sintético.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.mortality_tables import (
    qx_base_table,
    qx_annuitant_table,
    invalidity_incidence_table,
)

PRODUCTS = [
    "peculio",
    "pensao_por_morte",
    "renda_invalidez",
    "pensao_menor",
    "previdencia_longevidade",
    "previdencia_resgate",
]

# Capital segurado / renda de referência por produto (ordem de grandeza ilustrativa,
# não derivada de nenhuma carteira real).
_PRODUCT_BENEFIT_RANGE = {
    "peculio": (80_000, 600_000),
    "pensao_por_morte": (1_500, 8_000),        # renda mensal
    "renda_invalidez": (1_500, 7_000),         # renda mensal
    "pensao_menor": (800, 3_000),               # renda mensal
    "previdencia_longevidade": (1_200, 12_000),  # renda mensal de aposentadoria
    "previdencia_resgate": (20_000, 400_000),   # saldo acumulado
}

_ANNUITY_PRODUCTS = {"pensao_por_morte", "renda_invalidez", "pensao_menor", "previdencia_longevidade"}


def generate_policyholders(
    n: int,
    age_min: int = 18,
    age_max: int = 85,
    seed: int = 42,
) -> pd.DataFrame:
    """Gera a carteira base de segurados (1 linha por segurado) distribuída
    entre os produtos, com idade, sexo e valor de benefício de referência."""
    rng = np.random.default_rng(seed)

    sex = rng.choice(["male", "female"], size=n, p=[0.49, 0.51])
    # distribuição etária com maior massa entre 30-55 anos (perfil típico de
    # carteira ativa de previdência/risco em fase de contribuição)
    age = np.clip(rng.normal(loc=42, scale=12, size=n), age_min, age_max).astype(int)
    product = rng.choice(PRODUCTS, size=n, p=[0.30, 0.18, 0.14, 0.08, 0.20, 0.10])

    benefit = np.zeros(n)
    for p in PRODUCTS:
        mask = product == p
        low, high = _PRODUCT_BENEFIT_RANGE[p]
        benefit[mask] = rng.uniform(low, high, size=mask.sum())

    contribution_rate = rng.uniform(0.008, 0.02, size=n)  # % do benefício/saldo, ao mês

    df = pd.DataFrame(
        {
            "policy_id": np.arange(1, n + 1),
            "sex": sex,
            "entry_age": age,
            "product": product,
            "benefit_reference": np.round(benefit, 2),
            "monthly_contribution_rate": contribution_rate,
        }
    )
    return df


def build_monthly_exposure(
    policyholders: pd.DataFrame,
    start_date: str,
    end_date: str,
    seed: int = 42,
) -> pd.DataFrame:
    """Expande a carteira em uma base longitudinal mensal (uma linha por
    segurado por mês de exposição) — equivalente à "base de expostos" real.

    Implementação totalmente vetorizada (sem loop Python por segurado): cada
    segurado entra em um mês aleatório da janela e permanece exposto até o fim
    da janela — o módulo de sinistros trunca a exposição no mês do evento.
    """
    rng = np.random.default_rng(seed + 1)
    months = pd.date_range(start_date, end_date, freq="MS")
    n = len(policyholders)
    n_months = len(months)

    entry_idx = rng.integers(0, max(1, n_months - 6), size=n)
    lengths = n_months - entry_idx
    total = int(lengths.sum())

    group_start = np.concatenate([[0], np.cumsum(lengths)[:-1]])
    idx_within_group = np.arange(total) - np.repeat(group_start, lengths)

    month_index_in_calendar = np.repeat(entry_idx, lengths) + idx_within_group
    year_month = months.values[month_index_in_calendar]

    policy_id_rep = np.repeat(policyholders["policy_id"].to_numpy(), lengths)
    sex_rep = np.repeat(policyholders["sex"].to_numpy(), lengths)
    product_rep = np.repeat(policyholders["product"].to_numpy(), lengths)
    benefit_rep = np.repeat(policyholders["benefit_reference"].to_numpy(), lengths)
    contrib_rate_rep = np.repeat(policyholders["monthly_contribution_rate"].to_numpy(), lengths)
    entry_age_rep = np.repeat(policyholders["entry_age"].to_numpy(), lengths)

    age = entry_age_rep + (idx_within_group // 12)
    contribution = benefit_rep * contrib_rate_rep

    exposure = pd.DataFrame(
        {
            "policy_id": policy_id_rep,
            "sex": sex_rep,
            "product": product_rep,
            "year_month": year_month,
            "age": age,
            "benefit_reference": benefit_rep,
            "contribution": contribution,
        }
    )
    return exposure


def simulate_claims(exposure: pd.DataFrame, seed: int = 42) -> pd.DataFrame:
    """Simula sinistros/eventos mês a mês a partir da tábua de mortalidade (ou
    de invalidez), truncando a exposição do segurado no mês do evento. Isso é
    o que torna o dataset sintético internamente consistente: os sinistros
    observados devem, em expectativa, aproximar o A/E de ~100% quando calculado
    contra a MESMA tábua usada para gerá-los — e é exatamente essa verificação
    que o pipeline de experience_engine faz (ver tests/test_experience_engine.py).

    Implementação totalmente vetorizada (sem loop Python por segurado/mês):
    calcula a probabilidade de evento de cada linha de exposição de uma vez,
    sorteia todos os Bernoulli de uma vez, e usa soma cumulativa por apólice
    para identificar e truncar exatamente no primeiro mês de evento.
    """
    rng = np.random.default_rng(seed + 2)
    qx_male = qx_base_table("male")
    qx_female = qx_base_table("female")
    ix_male = invalidity_incidence_table("male")
    ix_female = invalidity_incidence_table("female")
    qx_annuitant_male = qx_annuitant_table("male")
    qx_annuitant_female = qx_annuitant_table("female")

    df = exposure.sort_values(["policy_id", "year_month"]).reset_index(drop=True).copy()

    is_male = (df["sex"] == "male").to_numpy()
    age = df["age"].to_numpy()
    product = df["product"].to_numpy()

    qx_mortality = np.where(is_male, qx_male(age), qx_female(age))
    ix_invalidity = np.where(is_male, ix_male(age), ix_female(age))
    qx_annuitant = np.where(is_male, qx_annuitant_male(age), qx_annuitant_female(age))

    p_event = np.select(
        [product == "renda_invalidez", product == "previdencia_longevidade", product == "previdencia_resgate"],
        [ix_invalidity / 12.0, qx_annuitant / 12.0, np.full_like(qx_mortality, 0.0025)],
        default=qx_mortality / 12.0,
    )

    success = rng.random(len(df)) < p_event
    df["success"] = success
    df["cum_success"] = df.groupby("policy_id")["success"].cumsum()

    first_event_mask = df["success"] & (df["cum_success"] == 1)
    keep_mask = (df["cum_success"] == 0) | first_event_mask
    kept_exposure = df.loc[keep_mask].drop(columns=["success", "cum_success"]).reset_index(drop=True)

    claims_raw = df.loc[first_event_mask].copy()
    claims = pd.DataFrame(
        {
            "policy_id": claims_raw["policy_id"].to_numpy(),
            "product": claims_raw["product"].to_numpy(),
            "sex": claims_raw["sex"].to_numpy(),
            "age_at_event": claims_raw["age"].to_numpy(),
            "occurrence_month": claims_raw["year_month"].to_numpy(),
            "report_lag_months": rng.integers(0, 3, size=len(claims_raw)),
            "benefit_reference": claims_raw["benefit_reference"].to_numpy(),
        }
    )

    return kept_exposure, claims


def build_synthetic_dataset(config: dict) -> dict:
    """Ponto de entrada único: gera carteira, exposição mensal e sinistros
    sintéticos consistentes, prontos para o pipeline de A/E e AR."""
    pconf = config["portfolio"]
    seed = config.get("seed", 42)

    policyholders = generate_policyholders(
        n=pconf["n_policyholders"],
        age_min=pconf["age_min"],
        age_max=pconf["age_max"],
        seed=seed,
    )
    exposure_raw = build_monthly_exposure(
        policyholders,
        start_date=pconf["start_date"],
        end_date=pconf["end_date"],
        seed=seed,
    )
    exposure, claims = simulate_claims(exposure_raw, seed=seed)
    return {
        "policyholders": policyholders,
        "exposure": exposure,
        "claims": claims,
    }
