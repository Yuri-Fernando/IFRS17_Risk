"""
Motor de Ajuste ao Risco (AR) — orquestra o cálculo final:

    QX_stress = fator_de_stress x QX_base
    BEL_stress = VPL(fluxos, QX_stress)
    BEL_base   = VPL(fluxos, QX_base)
    AR_componente = BEL_stress - BEL_base

    AR_total = soma das caixinhas - benefício de diversificação

Implementa também a direção de stress por tipo de risco (mortalidade vs.
longevidade, seção 3.7 da metodologia) e a estrutura de "caixinhas" com
diversificação (seção 3.8), que nunca foi implementada no projeto original
(gap #4).
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from src.actuarial.bel_calculator import compute_bel_for_product
from src.data.mortality_tables import qx_base_table, qx_annuitant_table, invalidity_incidence_table

# Direção do stress por produto: +1 = aumenta QX (mortalidade), -1 = reduz QX (longevidade)
STRESS_DIRECTION = {
    "peculio": +1,
    "pensao_por_morte": +1,
    "pensao_menor": +1,
    "renda_invalidez": +1,          # aumento na incidência de invalidez
    "previdencia_longevidade": -1,  # menos mortes = mais longevidade = mais passivo
}


@dataclass
class ComponentARResult:
    product: str
    bel_base: float
    bel_stress: float
    ar_monetary: float
    ar_pct_of_bel: float
    stress_factor: float
    target_percentile: int


def stressed_qx_function(base_qx_fn: callable, stress_factor: float, direction: int) -> callable:
    """Aplica o fator de stress na direção correta: multiplica o QX (mortalidade)
    ou divide (equivalente a reduzir o QX, para longevidade)."""
    def qx_stress(age):
        base = base_qx_fn(age)
        if direction > 0:
            return np.clip(base * stress_factor, 1e-6, 0.999)
        return np.clip(base / stress_factor, 1e-6, 0.999)

    return qx_stress


def compute_component_ar(
    product: str,
    policyholders: pd.DataFrame,
    stress_factor: float,
    target_percentile: int,
    discount_rate: float,
) -> ComponentARResult:
    direction = STRESS_DIRECTION.get(product, +1)

    if product == "previdencia_longevidade":
        qx_base_by_sex = {"male": qx_annuitant_table("male"), "female": qx_annuitant_table("female")}
    elif product == "renda_invalidez":
        qx_base_by_sex = {"male": invalidity_incidence_table("male"), "female": invalidity_incidence_table("female")}
    else:
        qx_base_by_sex = {"male": qx_base_table("male"), "female": qx_base_table("female")}

    qx_stress_by_sex = {
        sex: stressed_qx_function(fn, stress_factor, direction) for sex, fn in qx_base_by_sex.items()
    }

    bel_base = compute_bel_for_product(product, policyholders, qx_base_by_sex, discount_rate)
    bel_stress = compute_bel_for_product(product, policyholders, qx_stress_by_sex, discount_rate)

    ar_monetary = bel_stress.present_value - bel_base.present_value
    ar_pct = ar_monetary / bel_base.present_value if bel_base.present_value else float("nan")

    return ComponentARResult(
        product=product,
        bel_base=bel_base.present_value,
        bel_stress=bel_stress.present_value,
        ar_monetary=ar_monetary,
        ar_pct_of_bel=ar_pct,
        stress_factor=stress_factor,
        target_percentile=target_percentile,
    )


def combine_components(
    results: list[ComponentARResult],
    diversification_benefit: float = 0.15,
) -> dict:
    """Soma simples das caixinhas menos o benefício de diversificação
    (seção 3.8 da metodologia) — melhoria de rigor sobre o projeto original,
    que somava sem qualquer desconto de correlação."""
    total_bel_base = sum(r.bel_base for r in results)
    sum_simple_ar = sum(r.ar_monetary for r in results)
    ar_diversified = sum_simple_ar * (1 - diversification_benefit)

    return {
        "total_bel_base": total_bel_base,
        "ar_sum_simple": sum_simple_ar,
        "ar_diversified": ar_diversified,
        "diversification_benefit_pct": diversification_benefit,
        "ar_diversified_pct_of_bel": ar_diversified / total_bel_base if total_bel_base else float("nan"),
        "csm_reduction": ar_diversified,  # todo R$1 de AR reduz o CSM em R$1 (seção 1.1 da metodologia)
    }


def solvency_ii_benchmark_check(stress_factor: float, target_percentile: int, sii_shock: float = 0.15) -> dict:
    """Compara direcionalmente o fator de stress obtido com o choque padrão de
    mortalidade do Solvency II (99,5% de confiança a 1 ano) — replica a lógica
    de defesa documentada na metodologia (seção 2, Fase 6): um percentil menor
    que 99,5% deve produzir, por construção, um fator de stress proporcionalmente
    menor que o benchmark europeu."""
    implied_stress_pct = stress_factor - 1.0
    consistent_direction = (target_percentile < 99.5) and (implied_stress_pct < sii_shock)
    return {
        "our_stress_pct": implied_stress_pct,
        "our_confidence_level": target_percentile / 100.0,
        "solvency_ii_shock_pct": sii_shock,
        "solvency_ii_confidence_level": 0.995,
        "directionally_consistent": bool(consistent_direction),
        "interpretation": (
            "Consistente: percentil de confiança menor que o Solvency II (99,5%) produziu, "
            "como esperado, um stress proporcionalmente menor que o benchmark europeu."
            if consistent_direction
            else "Atenção: o stress obtido não segue a relação esperada frente ao benchmark Solvency II — revisar calibração."
        ),
    }
