"""Cálculo de métricas de risco."""

import numpy as np


def calculate_var(losses, alpha=95):
    """Calcula Value at Risk."""
    return np.percentile(losses, alpha)


def calculate_cte(losses, alpha=95):
    """Calcula Conditional Tail Expectation."""
    var = np.percentile(losses, alpha)
    return losses[losses >= var].mean()


def calculate_cost_of_capital(losses, alpha=95, cost_of_capital_rate=0.10):
    """Calcula Cost of Capital."""
    var = calculate_var(losses, alpha)
    mean_loss = np.mean(losses)
    return (var - mean_loss) * cost_of_capital_rate


def quantile_regression(losses, tau=0.95):
    """Regressão de quantil."""
    return np.quantile(losses, tau)
