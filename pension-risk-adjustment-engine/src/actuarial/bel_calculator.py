"""
Calculadora de BEL (Best Estimate Liabilities) por produto.

Implementa a lógica descrita em itau/METODOLOGIA_MESTRE.md seção 3.6 e 3.9:
- Peculio: valor presente esperado do pagamento único (lump sum).
- Produtos de renda (Pensão por Morte, Renda por Invalidez, Pensão ao Menor,
  Previdência-Longevidade): valor presente de uma anuidade contingente à
  tábua de decremento aplicável.

Aceita tanto a tábua base quanto a tábua estressada — é a mesma função chamada
duas vezes (QX_base e QX_stress) que gera BEL_base e BEL_stress, cuja diferença
é o AR monetário (ver src/risk_adjustment/ar_engine.py).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class BELResult:
    product: str
    present_value: float
    n_policies: int
    discount_rate: float


def _discount_factors(n_years: int, discount_rate: float) -> np.ndarray:
    years = np.arange(1, n_years + 1)
    return 1.0 / (1.0 + discount_rate) ** years


def bel_lump_sum(
    policyholders: pd.DataFrame,
    qx_fn_by_sex: dict[str, callable],
    discount_rate: float,
    max_projection_years: int = 45,
) -> BELResult:
    """BEL para produtos de pagamento único (Peculio): soma, para cada
    segurado, do valor esperado descontado de receber o capital segurado no
    ano em que a morte ocorreria, ponderado pela probabilidade de sobreviver
    até esse ano e morrer naquele ano específico."""
    total_pv = 0.0
    years = np.arange(1, max_projection_years + 1)
    discount = _discount_factors(max_projection_years, discount_rate)

    for sex, grp in policyholders.groupby("sex"):
        qx_fn = qx_fn_by_sex[sex]
        ages = grp["entry_age"].to_numpy()
        benefits = grp["benefit_reference"].to_numpy()

        # matriz idade x ano de projeção
        proj_ages = ages[:, None] + years[None, :]
        qx_matrix = qx_fn(proj_ages)
        survival = np.cumprod(1 - qx_matrix, axis=1)
        survival_prev = np.hstack([np.ones((len(ages), 1)), survival[:, :-1]])
        prob_death_in_year = survival_prev * qx_matrix

        pv_per_policy = (prob_death_in_year * discount[None, :]).sum(axis=1) * benefits
        total_pv += pv_per_policy.sum()

    return BELResult(product="peculio", present_value=float(total_pv), n_policies=len(policyholders), discount_rate=discount_rate)


def bel_annuity(
    policyholders: pd.DataFrame,
    qx_fn_by_sex: dict[str, callable],
    discount_rate: float,
    monthly_benefit_col: str = "benefit_reference",
    max_projection_years: int = 45,
) -> BELResult:
    """BEL para produtos de renda mensal contingente à sobrevivência
    (Pensão por Morte após o evento, Renda por Invalidez, Pensão ao Menor,
    Previdência-Longevidade): valor presente de uma anuidade mensal vitalícia
    (ou temporária, se aplicável) ponderada pela probabilidade de sobrevivência
    ano a ano."""
    total_pv = 0.0
    years = np.arange(1, max_projection_years + 1)
    discount = _discount_factors(max_projection_years, discount_rate)

    for sex, grp in policyholders.groupby("sex"):
        qx_fn = qx_fn_by_sex[sex]
        ages = grp["entry_age"].to_numpy()
        monthly_benefit = grp[monthly_benefit_col].to_numpy()
        annual_benefit = monthly_benefit * 12.0

        proj_ages = ages[:, None] + years[None, :]
        qx_matrix = qx_fn(proj_ages)
        survival = np.cumprod(1 - qx_matrix, axis=1)

        pv_per_policy = (survival * discount[None, :]).sum(axis=1) * annual_benefit
        total_pv += pv_per_policy.sum()

    return BELResult(product="annuity", present_value=float(total_pv), n_policies=len(policyholders), discount_rate=discount_rate)


# Fator de anuidade equivalente: converte a renda mensal em um "capital
# equivalente" pago no momento da entrada no benefício — simplificação
# atuarial deliberada (ver docstring de bel_contingent_annuity_lump_sum_equivalent).
_ANNUITY_EQUIVALENT_FACTOR_MONTHS = {
    "pensao_por_morte": 12 * 15,    # ~15 anos de duração média esperada do benefício ao beneficiário
    "renda_invalidez": 12 * 18,     # tende a ser mais longa (pode ser vitalícia desde idade mais jovem)
    "pensao_menor": 12 * 8,         # até a maioridade — duração tipicamente mais curta e limitada no tempo
}


def bel_contingent_annuity_lump_sum_equivalent(
    policyholders: pd.DataFrame,
    qx_fn_by_sex: dict[str, callable],
    discount_rate: float,
    annuity_equivalent_months: int,
    max_projection_years: int = 45,
) -> BELResult:
    """BEL para produtos em que o EVENTO estressado é a entrada no benefício
    (morte do titular para Pensão por Morte/Pensão ao Menor; invalidez para
    Renda por Invalidez) — não a sobrevivência do titular.

    Modelagem: no ano em que o evento ocorre, a empresa passa a dever o valor
    presente da renda subsequente ao beneficiário/segurado. Aproximamos esse
    valor presente por um "capital equivalente" fixo (renda mensal x fator de
    anuidade equivalente em meses) — simplificação deliberada que evita
    modelar um segundo decremento encadeado (sobrevivência do beneficiário
    após o evento), fora do escopo deste projeto de portfólio, mas que
    preserva a mecânica essencial: mais eventos de entrada (QX/incidência
    maior) implica mais capital equivalente devido, logo mais BEL — a mesma
    direção de um pagamento único (lump sum), com uma magnitude maior por
    evento (proporcional à duração esperada do benefício).
    """
    equivalent_capital = policyholders["benefit_reference"] * annuity_equivalent_months
    proxy = policyholders.assign(benefit_reference=equivalent_capital)
    result = bel_lump_sum(proxy, qx_fn_by_sex, discount_rate, max_projection_years)
    return BELResult(product=result.product, present_value=result.present_value, n_policies=result.n_policies, discount_rate=discount_rate)


def compute_bel_for_product(
    product: str,
    policyholders: pd.DataFrame,
    qx_fn_by_sex: dict[str, callable],
    discount_rate: float,
) -> BELResult:
    """Roteador conforme a natureza econômica de cada produto:

    - `previdencia_longevidade`: anuidade genuína — o titular já está na fase
      de renda e recebe enquanto sobrevive (QX menor = mais anos pagos).
    - `pensao_por_morte`, `renda_invalidez`, `pensao_menor`: o evento
      estressado é a ENTRADA no benefício (morte/invalidez do titular ainda
      ativo) — modelado como capital equivalente pago na entrada, não como
      anuidade de sobrevivência do titular (ver
      bel_contingent_annuity_lump_sum_equivalent).
    - demais produtos (`peculio`): pagamento único na morte (lump sum puro).
    """
    subset = policyholders[policyholders["product"] == product]
    if subset.empty:
        return BELResult(product=product, present_value=0.0, n_policies=0, discount_rate=discount_rate)

    if product == "previdencia_longevidade":
        return bel_annuity(subset, qx_fn_by_sex, discount_rate)
    if product in _ANNUITY_EQUIVALENT_FACTOR_MONTHS:
        return bel_contingent_annuity_lump_sum_equivalent(
            subset, qx_fn_by_sex, discount_rate, _ANNUITY_EQUIVALENT_FACTOR_MONTHS[product]
        )
    return bel_lump_sum(subset, qx_fn_by_sex, discount_rate)
