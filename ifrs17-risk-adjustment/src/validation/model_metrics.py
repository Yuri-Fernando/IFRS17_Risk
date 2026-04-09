"""Métricas de desempenho do modelo."""

import numpy as np


def calculate_all_metrics(actual, predicted):
    """Calcula todas as métricas de desempenho."""
    actual = np.array(actual)
    predicted = np.array(predicted)

    rmse = np.sqrt(np.mean((actual - predicted) ** 2))
    mae = np.mean(np.abs(actual - predicted))
    mape = np.mean(np.abs((actual - predicted) / (actual + 1e-8))) * 100
    mse = np.mean((actual - predicted) ** 2)
    
    ss_res = np.sum((actual - predicted) ** 2)
    ss_tot = np.sum((actual - np.mean(actual)) ** 2)
    r2 = 1 - (ss_res / (ss_tot + 1e-8))
    
    mbe = np.mean(actual - predicted)

    return {'rmse': rmse, 'mae': mae, 'mape': mape, 'mse': mse, 'r2': r2, 'mbe': mbe}
