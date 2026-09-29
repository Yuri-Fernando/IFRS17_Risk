"""PD bayesiana por segmento (Beta-Binomial) com shrinkage.

Prior Beta(α, β) por Bayes empírico (método dos momentos entre segmentos);
posterior Beta(α + d, β + n − d). Segmentos pequenos são puxados para a média
da carteira — mesma intuição da credibilidade de Bühlmann usada na v3 atuarial
deste repositório (Z = n / (n + α + β)).
"""

from __future__ import annotations

import numpy as np
import pandas as pd
from scipy.stats import beta as beta_dist


def empirical_bayes_prior(defaults: np.ndarray, n: np.ndarray) -> tuple[float, float]:
    rates = defaults / n
    w = n / n.sum()
    m = float(np.sum(w * rates))
    v = float(np.sum(w * (rates - m) ** 2))
    v_binom = float(np.sum(w * m * (1 - m) / n))  # parte da variância explicada por amostragem
    between = max(v - v_binom, 1e-6)
    k = max(m * (1 - m) / between - 1, 1.0)  # α+β
    return m * k, (1 - m) * k


def beta_binomial_pd(df: pd.DataFrame, seg_col: str, n_col: str = "n", d_col: str = "defaults",
                     level: float = 0.90) -> pd.DataFrame:
    a0, b0 = empirical_bayes_prior(df[d_col].to_numpy(float), df[n_col].to_numpy(float))
    out = df.copy()
    a = a0 + out[d_col]
    b = b0 + out[n_col] - out[d_col]
    lo, hi = (1 - level) / 2, 1 - (1 - level) / 2
    out["raw_pd"] = out[d_col] / out[n_col]
    out["posterior_mean"] = a / (a + b)
    out["ci_low"] = beta_dist.ppf(lo, a, b)
    out["ci_high"] = beta_dist.ppf(hi, a, b)
    out["credibility_Z"] = out[n_col] / (out[n_col] + a0 + b0)
    out["prior_alpha"], out["prior_beta"] = a0, b0
    return out.sort_values(seg_col).reset_index(drop=True)
