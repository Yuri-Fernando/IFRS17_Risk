"""Simulação Monte Carlo."""

import numpy as np


def simulate_losses(freq_model, sev_model, n_simulations=10000, seed=42):
    """Simula perdas agregadas via Monte Carlo."""
    np.random.seed(seed)
    losses = []

    for _ in range(n_simulations):
        n_events = freq_model.sample(1)[0]
        if n_events > 0:
            event_values = sev_model.sample(n_events)
            total_loss = np.sum(event_values)
        else:
            total_loss = 0
        losses.append(total_loss)

    return np.array(losses)


def convergence_analysis(freq_model, sev_model, sizes):
    """Analisa convergência das simulações."""
    convergence = {}
    for size in sizes:
        losses = simulate_losses(freq_model, sev_model, n_simulations=size, seed=42)
        convergence[size] = {'mean': np.mean(losses), 'std': np.std(losses)}
    return convergence


def simulate_with_confidence_interval(freq_model, sev_model, n_simulations=10000, ci=0.95):
    """Simula com intervalo de confiança."""
    losses = simulate_losses(freq_model, sev_model, n_simulations=n_simulations)
    mean = np.mean(losses)
    std_err = np.std(losses) / np.sqrt(n_simulations)
    z = 1.96  # 95% CI
    ci_lower = mean - z * std_err
    ci_upper = mean + z * std_err
    return {'losses': losses, 'mean': mean, 'ci_lower': ci_lower, 'ci_upper': ci_upper}
