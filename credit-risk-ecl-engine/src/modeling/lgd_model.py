"""
Modelagem de LGD (Loss Given Default).

O dataset German Credit não traz valores de recuperação pós-default
(não é um dataset de workout/cobrança). Para manter o PoC honesto sobre
essa limitação — e ainda assim demonstrar a técnica esperada em produção —
o LGD é modelado em duas camadas:

1. **LGD base por segmento de colateral** (`property`): garantias reais
   (imóvel) reduzem a severidade da perda; ausência de garantia a eleva.
   Isso segue a lógica de mitigadores de risco exigida em IFRS 9 §5.5.17,
   sem inventar uma distribuição arbitrária — os multiplicadores refletem
   ordenação de risco coerente com a hierarquia de garantias do próprio
   dataset (`property`).
2. **Downturn LGD add-on**: componente adicional aplicado em cenário de
   estresse (stress testing), simulando a exigência regulatória de LGD
   sensível ao ciclo econômico (point-in-time vs. through-the-cycle).

A incerteza da severidade é capturada com uma distribuição Beta, adequada
por ser limitada a [0, 1] — via de regra utilizada em modelos de LGD de
mercado.
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy import stats

# Severidade média por tipo de garantia (0 = perda total, 1 = perda nula).
# Ordenação: imóvel > seguro/poupança vinculada > veículo/outros > sem garantia.
_LGD_MEAN_BY_COLLATERAL = {
    "real estate": 0.30,
    "building society savings/life insurance": 0.40,
    "car or other": 0.55,
    "unknown/no property": 0.65,
}

_LGD_STD_BY_COLLATERAL = {
    "real estate": 0.08,
    "building society savings/life insurance": 0.10,
    "car or other": 0.12,
    "unknown/no property": 0.15,
}


def _beta_params(mean: float, std: float) -> tuple[float, float]:
    """Converte média/desvio-padrão desejados nos parâmetros (a, b) da
    distribuição Beta correspondente (método dos momentos)."""
    var = std**2
    common = mean * (1 - mean) / var - 1
    a = mean * common
    b = (1 - mean) * common
    return max(a, 0.5), max(b, 0.5)


def estimate_lgd(df: pd.DataFrame, downturn_addon: float = 0.0, seed: int = 11) -> np.ndarray:
    """Estima o LGD esperado de cada contrato via amostragem Beta em
    torno da média do segmento de colateral (`property`).

    Parameters
    ----------
    downturn_addon: acréscimo aplicado à média de LGD (usado no stress test
        para simular LGD "downturn" em cenário adverso).
    """
    rng = np.random.default_rng(seed)
    lgd = np.zeros(len(df))

    for collateral, mean in _LGD_MEAN_BY_COLLATERAL.items():
        mask = df["property"].values == collateral
        if not mask.any():
            continue
        std = _LGD_STD_BY_COLLATERAL[collateral]
        adj_mean = float(np.clip(mean + downturn_addon, 0.05, 0.95))
        a, b = _beta_params(adj_mean, std)
        lgd[mask] = stats.beta.rvs(a, b, size=mask.sum(), random_state=rng)

    # fallback para categorias não mapeadas
    unmapped = lgd == 0
    if unmapped.any():
        lgd[unmapped] = np.clip(0.55 + downturn_addon, 0.05, 0.95)

    return np.clip(lgd, 0.01, 0.99)
