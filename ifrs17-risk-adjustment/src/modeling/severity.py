"""Modelo de Severidade (Lognormal/Gamma)."""

import numpy as np
from scipy import stats


class SeverityModel:
    def __init__(self, distribution='lognormal', params=None):
        self.distribution = distribution
        self.params = params or {'mu': 1.0, 'sigma': 0.5}

    def fit(self, data):
        """Ajusta distribuição aos dados."""
        data = np.array(data)
        data = data[data > 0]  # Remove zeros/negativos
        
        if len(data) > 0:
            self.params['mu'] = np.log(np.mean(data))
            self.params['sigma'] = np.std(np.log(data))
        return self

    def sample(self, n=1):
        """Gera amostras."""
        mu = self.params.get('mu', 1.0)
        sigma = self.params.get('sigma', 0.5)
        return np.random.lognormal(mu, sigma, n)


def train_severity(data, distribution='lognormal'):
    """Treina modelo de severidade."""
    # Usa valores numéricos do dataset
    numeric_cols = data.select_dtypes(include=[np.number]).columns
    if len(numeric_cols) > 0:
        sev_data = data[numeric_cols[0]].values
    else:
        sev_data = np.random.lognormal(mean=1, sigma=1, size=len(data))

    model = SeverityModel(distribution=distribution)
    model.fit(sev_data)
    return model
