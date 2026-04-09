"""Modelo de Frequência (Poisson/Negative Binomial)."""

import numpy as np
from scipy import stats


class FrequencyModel:
    def __init__(self, distribution='poisson', lambda_param=1.0):
        self.distribution = distribution
        self.lambda_param = lambda_param
        self.params = {'lambda': lambda_param}

    def fit(self, data):
        """Ajusta distribuição aos dados."""
        self.lambda_param = np.mean(data)
        self.params = {'lambda': self.lambda_param}
        return self

    def sample(self, n=1):
        """Gera amostras."""
        return np.random.poisson(self.lambda_param, n)


def train_frequency(data, distribution='poisson'):
    """Treina modelo de frequência."""
    # Se houver coluna de sinistros, usa; senão gera frequência
    if 'claim_status' in data.columns:
        freq_data = (data['claim_status'] > 0).astype(int)
    else:
        freq_data = np.random.poisson(2, size=len(data))

    model = FrequencyModel(distribution=distribution)
    model.fit(freq_data)
    return model
