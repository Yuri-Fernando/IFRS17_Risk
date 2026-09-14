"""
Simulação de Monte Carlo da perda agregada da carteira com correlação
entre segmentos via cópula Gaussiana.

Por que isso importa (contexto do projeto)
-------------------------------------------
Um modelo de ECL que soma `PD x LGD x EAD` contrato a contrato assume,
implicitamente, independência entre inadimplências. Em uma carteira real
isso subestima o risco de cauda: choques macroeconômicos (desemprego,
juros, crédito) afetam vários segmentos ao mesmo tempo, então os defaults
são positivamente correlacionados. Ignorar essa correlação é uma
simplificação comum e conhecida em PoCs de risco — e é justamente o gap
que este módulo resolve, incorporando dependência entre os drivers de
risco por meio de uma cópula Gaussiana multivariada.

Método
------
1. Cada segmento de portfólio (`assign_segment`) tem uma PD média (ponto
   de partida: a PD 12m média do segmento, vinda do modelo de PD).
2. Amostram-se choques sistêmicos correlacionados Z ~ N(0, Σ), onde Σ é a
   matriz de correlação entre segmentos (parametrizável em
   `config/parameters.yaml`).
3. Cada choque Z_i desloca a PD do segmento i via a fórmula de mistura de
   Vasicek (base do modelo IRB de Basileia):

       PD_i(Z) = Φ( (Φ⁻¹(PD_i) + sqrt(ρ_i) * Z_i) / sqrt(1 - ρ_i) )

   onde ρ_i é a correlação de ativos do segmento (asset correlation).
4. Dentro de cada cenário, cada contrato do segmento tem seu default
   sorteado com Bernoulli(PD_i(Z)), e a perda do cenário é
   Σ (default_j * LGD_j * EAD_j).
5. Repete-se N vezes → distribuição de perda agregada da carteira, da
   qual se extraem VaR e CVaR (Expected Shortfall) em um nível de
   confiança dado — métricas usadas para dimensionar capital econômico
   e complementar a ECL contábil (que é uma esperança, não uma medida de
   cauda).
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy.stats import norm


@dataclass
class CopulaSimulationResult:
    losses: np.ndarray                 # perda agregada por cenário (n_simulations,)
    expected_loss: float
    var: dict[str, float]              # VaR por nível de confiança
    cvar: dict[str, float]             # CVaR (Expected Shortfall) por nível de confiança
    diversification_benefit: float     # ECL somada (independência) - EL simulado (correlacionado)
    correlation_matrix: pd.DataFrame
    segments: list[str]


def _build_correlation_matrix(segments: list[str], correlation: float) -> np.ndarray:
    """Matriz de correlação equicorrelacionada entre segmentos.

    Uma correlação única simplifica a calibração no PoC; em produção essa
    matriz seria estimada a partir de séries históricas de inadimplência
    por segmento (correlação de Pearson/Spearman entre taxas de default).
    """
    n = len(segments)
    corr = np.full((n, n), correlation)
    np.fill_diagonal(corr, 1.0)
    return corr


def simulate_portfolio_losses(
    df_ecl: pd.DataFrame,
    n_simulations: int = 10000,
    inter_segment_correlation: float = 0.25,
    asset_correlation: float = 0.15,
    confidence_levels: tuple[float, ...] = (0.95, 0.999),
    seed: int = 123,
) -> CopulaSimulationResult:
    rng = np.random.default_rng(seed)

    segments = sorted(df_ecl["segment"].unique().tolist())
    seg_to_idx = {s: i for i, s in enumerate(segments)}
    n_segments = len(segments)

    seg_idx = df_ecl["segment"].map(seg_to_idx).values
    pd_i = df_ecl["pd_used"].values.astype(float)
    lgd_i = df_ecl["lgd"].values.astype(float)
    ead_i = df_ecl["ead"].values.astype(float)

    pd_i = np.clip(pd_i, 1e-4, 1 - 1e-4)
    pd_inv_norm = norm.ppf(pd_i)  # Φ⁻¹(PD) por contrato

    corr_matrix = _build_correlation_matrix(segments, inter_segment_correlation)
    chol = np.linalg.cholesky(corr_matrix)

    losses = np.empty(n_simulations)
    sqrt_rho = np.sqrt(asset_correlation)
    sqrt_1m_rho = np.sqrt(1 - asset_correlation)

    for s in range(n_simulations):
        z_segments = chol @ rng.standard_normal(n_segments)      # choque sistêmico correlacionado por segmento
        z_contract = z_segments[seg_idx]                          # projeta para cada contrato do segmento
        pd_scenario = norm.cdf((pd_inv_norm + sqrt_rho * z_contract) / sqrt_1m_rho)

        defaults = rng.uniform(size=len(pd_scenario)) < pd_scenario
        losses[s] = np.sum(defaults * lgd_i * ead_i)

    expected_loss = float(losses.mean())
    var = {f"var_{int(cl*1000)/10:g}": float(np.quantile(losses, cl)) for cl in confidence_levels}
    cvar = {
        f"cvar_{int(cl*1000)/10:g}": float(losses[losses >= np.quantile(losses, cl)].mean())
        for cl in confidence_levels
    }

    ecl_independent_sum = float((pd_i * lgd_i * ead_i).sum())
    diversification_benefit = ecl_independent_sum - expected_loss

    return CopulaSimulationResult(
        losses=losses,
        expected_loss=expected_loss,
        var=var,
        cvar=cvar,
        diversification_benefit=diversification_benefit,
        correlation_matrix=pd.DataFrame(corr_matrix, index=segments, columns=segments),
        segments=segments,
    )
