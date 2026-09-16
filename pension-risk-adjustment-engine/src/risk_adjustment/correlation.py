"""
Cenário de correlação adversa entre longevidade, conversão em renda e resgate
(itau/METODOLOGIA_MESTRE.md, seção 3.7 e proposta de melhoria seção 8, item 3).

O projeto original descreveu qualitativamente que o cenário mais adverso para
o AR de um produto de renda vitalícia não é estressar cada premissa
isoladamente, mas a combinação correlacionada de: mortalidade caindo
(pessoas vivem mais), taxa de conversão em renda subindo (mais saldo migra
para a fase vitalícia) e taxa de resgate caindo (mais gente permanece até a
conversão). Essa simulação conjunta nunca foi implementada (gap #7).

Aqui implementamos via cópula Gaussiana — a mesma técnica já usada no projeto
v2 do repositório (credit-risk-ecl-engine) para correlacionar segmentos de
risco de crédito — trazendo a mesma ferramenta estatística para o domínio
atuarial de previdência, o que reforça a continuidade metodológica entre os
dois projetos do portfólio.
"""
from __future__ import annotations

from dataclasses import dataclass

import numpy as np
from scipy import stats


@dataclass
class AdverseScenarioResult:
    n_scenarios: int
    longevity_shift: np.ndarray       # multiplicador sobre QX (menor que 1 = mais longevidade)
    conversion_shift: np.ndarray      # multiplicador sobre a taxa de conversão
    lapse_shift: np.ndarray           # multiplicador sobre a taxa de resgate
    percentile_used: int

    def summary(self) -> dict:
        return {
            "longevity_shift_p50": float(np.percentile(self.longevity_shift, 50)),
            "longevity_shift_pXX": float(np.percentile(self.longevity_shift, self.percentile_used)),
            "conversion_shift_p50": float(np.percentile(self.conversion_shift, 50)),
            "conversion_shift_pXX": float(np.percentile(self.conversion_shift, self.percentile_used)),
            "lapse_shift_p50": float(np.percentile(self.lapse_shift, 50)),
            "lapse_shift_pXX": float(np.percentile(self.lapse_shift, self.percentile_used)),
        }


def simulate_adverse_correlation_scenario(
    n_scenarios: int,
    corr_longevity_conversion: float,
    corr_longevity_lapse: float,
    target_percentile: int = 80,
    seed: int = 42,
    longevity_vol: float = 0.08,
    conversion_vol: float = 0.10,
    lapse_vol: float = 0.15,
) -> AdverseScenarioResult:
    """Simula 3 variáveis correlacionadas (choques de longevidade, conversão e
    resgate) via cópula Gaussiana: gera normais padrão correlacionadas,
    transforma em multiplicadores log-normais centrados em 1.0 com a
    volatilidade informada."""
    rng = np.random.default_rng(seed)

    corr_conversion_lapse = -0.30  # conversão alta e resgate baixo tendem a andar juntos (mesmo regime de permanência)
    cov = np.array(
        [
            [1.0, corr_longevity_conversion, corr_longevity_lapse],
            [corr_longevity_conversion, 1.0, corr_conversion_lapse],
            [corr_longevity_lapse, corr_conversion_lapse, 1.0],
        ]
    )
    mean = np.zeros(3)
    z = rng.multivariate_normal(mean, cov, size=n_scenarios)
    u = stats.norm.cdf(z)  # transforma em uniformes correlacionadas (cópula Gaussiana)

    # longevidade: quantil da normal(1, vol) -> queda de QX (multiplicador < 1 = mais longevidade)
    longevity_shift = stats.norm.ppf(u[:, 0], loc=1.0, scale=longevity_vol)
    conversion_shift = stats.norm.ppf(u[:, 1], loc=1.0, scale=conversion_vol)
    lapse_shift = stats.norm.ppf(u[:, 2], loc=1.0, scale=lapse_vol)

    return AdverseScenarioResult(
        n_scenarios=n_scenarios,
        longevity_shift=np.clip(longevity_shift, 0.5, 1.5),
        conversion_shift=np.clip(conversion_shift, 0.5, 1.8),
        lapse_shift=np.clip(lapse_shift, 0.3, 2.0),
        percentile_used=target_percentile,
    )
