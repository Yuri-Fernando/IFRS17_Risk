"""Modelo de Lapse (Cancelamento)."""

import numpy as np


def calculate_lapse_rate(duration, age=None, base_rate=0.05):
    """Calcula taxa de cancelamento."""
    return base_rate * (1 + 0.02 * duration)


def gompertz_lapse(t, a=0.05, b=0.1):
    """Função de Gompertz para lapse."""
    return a * np.exp(b * t)


def logistic_lapse(t, L=1, k=0.5, t0=5):
    """Função logística para lapse."""
    return L / (1 + np.exp(-k * (t - t0)))
