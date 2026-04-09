"""Cálculo de Risk Adjustment."""

import numpy as np


def calculate_risk_adjustment(losses, method='var', alpha=95, include_all_methods=False):
    """Calcula Risk Adjustment com diferentes métodos."""
    mean_loss = np.mean(losses)
    std_loss = np.std(losses)
    min_loss = np.min(losses)
    max_loss = np.max(losses)

    # VaR
    var_value = np.percentile(losses, alpha)
    ra_var = var_value - mean_loss

    # CTE
    var_losses = losses[losses >= var_value]
    cte_value = var_losses.mean() if len(var_losses) > 0 else var_value
    ra_cte = cte_value - mean_loss

    # Cost of Capital
    ra_coc = ra_var * 0.10

    result = {
        'method': method,
        'method_description': f'{method.upper()} {alpha}%',
        'alpha': alpha,
        'mean_loss': mean_loss,
        'std_loss': std_loss,
        'min_loss': min_loss,
        'max_loss': max_loss,
        'Risk_Adjustment': ra_var if method == 'var' else (ra_cte if method == 'cte' else ra_coc),
    }

    if include_all_methods:
        result['all_methods_comparison'] = {
            'VaR': ra_var,
            'CTE': ra_cte,
            'Cost of Capital': ra_coc,
        }

    return result
