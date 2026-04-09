"""Testes de aderência de distribuição."""

import numpy as np
from scipy import stats


def ks_test(data, distribution='lognormal'):
    """Kolmogorov-Smirnov test."""
    data = np.array(data)
    data = data[data > 0]

    if distribution == 'lognormal':
        log_data = np.log(data)
        ks_stat, p_value = stats.kstest(log_data, 'norm')
    else:
        ks_stat, p_value = stats.kstest(data, 'norm')

    return {
        'distribution': distribution,
        'ks_statistic': ks_stat,
        'p_value': p_value,
        'reject_h0': p_value < 0.05,
        'conclusion': 'Rejeita normalidade' if p_value < 0.05 else 'Não rejeita normalidade'
    }


def anderson_darling_test(data):
    """Anderson-Darling test."""
    result = stats.anderson(data)
    return {'statistic': result.statistic, 'critical_values': result.critical_values}


def shapiro_wilk_test(data):
    """Shapiro-Wilk test."""
    stat, p_value = stats.shapiro(data)
    return {'statistic': stat, 'p_value': p_value}


def jarque_bera_test(data):
    """Jarque-Bera test."""
    stat, p_value = stats.jarque_bera(data)
    return {'statistic': stat, 'p_value': p_value}
