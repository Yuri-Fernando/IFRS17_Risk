"""Teste de estresse."""

import numpy as np


def stress_test(losses, scenarios):
    """Teste de estresse geral."""
    results = {}
    for scenario, factor in scenarios.items():
        stressed = losses * factor
        results[scenario] = {'mean': np.mean(stressed), 'std': np.std(stressed)}
    return results


def claims_frequency_stress(base_frequency, factors):
    """Estresse na frequência de sinistros."""
    results = {}
    for i, factor in enumerate(factors):
        stressed_freq = base_frequency * factor
        results[f'Scenario_{i+1}'] = {'stressed_frequency': stressed_freq}
    return results


def claims_severity_stress(base_severity, factors):
    """Estresse na severidade de sinistros."""
    results = {}
    for i, factor in enumerate(factors):
        stressed_sev = base_severity * factor
        results[f'Scenario_{i+1}'] = {'stressed_severity': stressed_sev}
    return results


def combined_stress(freq_model, sev_model, freq_factors, sev_factors):
    """Estresse combinado."""
    return {'combined': 'stress test'}


def reverse_stress_test(target_loss, freq_model, sev_model):
    """Reverse stress test."""
    return {'target': target_loss, 'feasible': True}
