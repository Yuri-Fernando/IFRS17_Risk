"""
Motor de Simulação de Monte Carlo para calibração do fator de stress do AR.

Reproduz fielmente a mecânica documentada em itau/METODOLOGIA_MESTRE.md,
seção 3.5: para cada cenário, gera uma série sintética do tamanho da janela
histórica (cada mês é zero com probabilidade p0, ou amostrado da distribuição
ajustada caso contrário), calcula a média da série simulada, e repete N vezes.
O fator de stress é o percentil-alvo dividido pela mediana (P50) da
distribuição de médias simuladas.

Toda premissa (p0, distribuição, parâmetros, semente) é retornada explicitamente
no resultado — nunca implícita — atendendo ao requisito de rastreabilidade
levantado como lição central do projeto original (seção 2, Fase 5).
"""
from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
from scipy import stats


@dataclass
class MonteCarloResult:
    n_scenarios: int
    window_months: int
    zero_probability: float
    distribution: str
    distribution_params: tuple
    seed: int
    simulated_means: np.ndarray = field(repr=False)
    median_simulated: float = 0.0
    percentiles: dict = field(default_factory=dict)

    def stress_factor(self, target_percentile: int) -> float:
        p_target = self.percentiles[target_percentile]
        return p_target / self.median_simulated

    def ar_points(self, target_percentile: int) -> float:
        return self.percentiles[target_percentile] - self.median_simulated

    def cte(self, target_percentile: int) -> float:
        """Conditional Tail Expectation — média das simulações acima do
        percentil-alvo. Usada como validação cruzada do percentil (proposta de
        melhoria da metodologia, seção 8 item 4)."""
        threshold = self.percentiles[target_percentile]
        tail = self.simulated_means[self.simulated_means >= threshold]
        return float(tail.mean()) if len(tail) else float("nan")


def estimate_zero_probability(historical_series: np.ndarray) -> float:
    """Estima p0 (probabilidade empírica de um mês com valor zero) diretamente
    da série histórica — documentado como estimativa empírica, não como
    premissa arbitrária do analista (correção da lição de processo da
    metodologia original, onde p0 foi fixado por decisão pessoal sem
    verificação estatística prévia)."""
    historical_series = np.asarray(historical_series, dtype=float)
    if len(historical_series) == 0:
        return 0.0
    return float(np.mean(historical_series == 0))


def run_monte_carlo(
    historical_series: np.ndarray,
    distribution: str = "gamma",
    n_scenarios: int = 10_000,
    window_months: int | None = None,
    seed: int = 42,
    zero_probability: float | None = None,
    target_percentiles: tuple[int, ...] = (75, 80, 90),
) -> MonteCarloResult:
    historical_series = np.asarray(historical_series, dtype=float)
    window_months = window_months or len(historical_series)
    p0 = zero_probability if zero_probability is not None else estimate_zero_probability(historical_series)

    positive_values = historical_series[historical_series > 0]
    dist = getattr(stats, distribution)
    params = dist.fit(positive_values, floc=0) if distribution in ("gamma", "lognorm") else dist.fit(positive_values)

    rng = np.random.default_rng(seed)
    zero_draws = rng.random((n_scenarios, window_months)) < p0
    sampled_values = dist.rvs(*params, size=(n_scenarios, window_months), random_state=rng)
    scenario_matrix = np.where(zero_draws, 0.0, sampled_values)
    simulated_means = scenario_matrix.mean(axis=1)

    median_simulated = float(np.percentile(simulated_means, 50))
    percentiles = {p: float(np.percentile(simulated_means, p)) for p in target_percentiles}

    return MonteCarloResult(
        n_scenarios=n_scenarios,
        window_months=window_months,
        zero_probability=p0,
        distribution=distribution,
        distribution_params=params,
        seed=seed,
        simulated_means=simulated_means,
        median_simulated=median_simulated,
        percentiles=percentiles,
    )


def convergence_test(
    historical_series: np.ndarray,
    distribution: str,
    scenario_sizes: list[int],
    target_percentile: int,
    seed: int = 42,
    tolerance: float = 0.01,
) -> tuple[list[dict], bool]:
    """Roda a simulação com quantidades crescentes de cenários e verifica se
    o fator de stress estabiliza (variação < tolerância entre o maior e o
    penúltimo tamanho testado) — proposta de melhoria da metodologia (seção 8,
    item 5), nunca formalmente documentada no projeto original."""
    records = []
    for n in scenario_sizes:
        result = run_monte_carlo(
            historical_series,
            distribution=distribution,
            n_scenarios=n,
            seed=seed,
            target_percentiles=(target_percentile,),
        )
        records.append({"n_scenarios": n, "stress_factor": result.stress_factor(target_percentile)})

    converged = False
    if len(records) >= 2:
        last, prev = records[-1]["stress_factor"], records[-2]["stress_factor"]
        converged = abs(last - prev) / abs(prev) < tolerance if prev != 0 else False

    return records, converged
