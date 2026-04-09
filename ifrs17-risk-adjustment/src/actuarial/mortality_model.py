"""Modelo de Mortalidade."""

import numpy as np


def calculate_mortality(age, base_rate=0.001):
    """Calcula taxa de mortalidade por idade."""
    return base_rate * (1.1 ** ((age - 40) / 10))


def gompertz_mortality(age, a=0.0005, b=0.08):
    """Função de Gompertz para mortalidade."""
    return a * np.exp(b * age)


def makeham_mortality(age, a=0.0005, b=0.08, c=0.01):
    """Função de Makeham para mortalidade."""
    return a + c * (b ** age)
