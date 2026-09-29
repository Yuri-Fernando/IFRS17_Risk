"""Survival analysis para tempo até default → lifetime PD (IFRS 9 §5.5.3).

- Kaplan-Meier (não paramétrico), com IC de Greenwood; eventos concorrentes
  (pré-pagamento, vencimento) tratados como censura — premissa documentada:
  KM então estima a PD "na ausência de saída", que superestima a PD
  observável quando há muito pré-pagamento (ver `cumulative_incidence`).
- Cox PH (statsmodels PHReg, Breslow) com covariáveis estáticas.
- Weibull AFT por máxima verossimilhança com censura (scipy).
- Aalen-Johansen simplificado (incidência cumulativa com risco competitivo).
Implementação própria/statsmodels para não depender de lifelines.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd
from scipy import optimize
from statsmodels.duration.hazard_regression import PHReg


# ---------------------------------------------------------------- Kaplan-Meier
def kaplan_meier(durations, events, horizon: int | None = None) -> pd.DataFrame:
    d = np.asarray(durations, dtype=int)
    e = np.asarray(events, dtype=int)
    T = int(horizon or d.max())
    rows, S, var_sum = [], 1.0, 0.0
    for t in range(1, T + 1):
        at_risk = int((d >= t).sum())
        ev = int(((d == t) & (e == 1)).sum())
        if at_risk > 0 and ev > 0:
            S *= 1 - ev / at_risk
            if at_risk > ev:
                var_sum += ev / (at_risk * (at_risk - ev))
        se = S * np.sqrt(var_sum)
        rows.append({"t": t, "at_risk": at_risk, "events": ev, "survival": S,
                     "cum_pd": 1 - S, "cum_pd_ci_low": max(0.0, 1 - S - 1.96 * se),
                     "cum_pd_ci_high": min(1.0, 1 - S + 1.96 * se)})
    return pd.DataFrame(rows)


def cumulative_incidence(durations, events, competing, horizon: int) -> pd.DataFrame:
    """Incidência cumulativa de default com risco competitivo (saída antecipada)."""
    d = np.asarray(durations, dtype=int)
    e = np.asarray(events, dtype=int)
    c = np.asarray(competing, dtype=int)
    S_all, cif, rows = 1.0, 0.0, []
    for t in range(1, horizon + 1):
        n = (d >= t).sum()
        if n == 0:
            rows.append({"t": t, "cif_default": cif})
            continue
        ev = ((d == t) & (e == 1)).sum()
        comp = ((d == t) & (c == 1)).sum()
        cif += S_all * ev / n
        S_all *= 1 - (ev + comp) / n
        rows.append({"t": t, "cif_default": cif})
    return pd.DataFrame(rows)


# ---------------------------------------------------------------- Weibull AFT
@dataclass
class WeibullAFT:
    beta: np.ndarray
    log_sigma: float
    columns: list[str]
    loglik: float

    @property
    def shape(self) -> float:
        return float(1 / np.exp(self.log_sigma))

    def survival(self, X: pd.DataFrame, t: np.ndarray) -> np.ndarray:
        lam = np.exp(_design(X, self.columns) @ self.beta)
        return np.exp(-(np.asarray(t)[None, :] / lam[:, None]) ** self.shape)


def _design(X: pd.DataFrame, columns: list[str]) -> np.ndarray:
    return np.column_stack([np.ones(len(X)), X[columns].to_numpy(float)])


def fit_weibull_aft(X: pd.DataFrame, durations, events) -> WeibullAFT:
    """log T = xβ + σW, W ~ Gumbel mínimo. Censura à direita no log-likelihood."""
    cols = list(X.columns)
    A = _design(X, cols)
    t = np.asarray(durations, dtype=float)
    e = np.asarray(events, dtype=float)
    logt = np.log(t)

    def nll(theta):
        b, ls = theta[:-1], theta[-1]
        s = np.exp(ls)
        z = (logt - A @ b) / s
        ll = e * (z - np.log(s) - logt) - np.exp(z)
        return -ll.sum()

    x0 = np.zeros(A.shape[1] + 1)
    x0[0] = np.log(t.mean() * 3)
    res = optimize.minimize(nll, x0, method="BFGS")
    return WeibullAFT(res.x[:-1], float(res.x[-1]), cols, float(-res.fun))


# ---------------------------------------------------------------- Cox PH
@dataclass
class CoxPH:
    params: np.ndarray
    bse: np.ndarray
    columns: list[str]
    baseline_times: np.ndarray
    baseline_cumhaz: np.ndarray

    def survival(self, X: pd.DataFrame, t: np.ndarray) -> np.ndarray:
        lp = X[self.columns].to_numpy(float) @ self.params
        H0 = np.interp(np.asarray(t, dtype=float), self.baseline_times, self.baseline_cumhaz, left=0.0)
        return np.exp(-H0[None, :] * np.exp(lp)[:, None])

    def summary(self) -> pd.DataFrame:
        return pd.DataFrame({"covariate": self.columns, "coef": self.params, "se": self.bse,
                             "hazard_ratio": np.exp(self.params)})


def fit_cox(X: pd.DataFrame, durations, events) -> CoxPH:
    cols = list(X.columns)
    m = PHReg(np.asarray(durations, float), X[cols].to_numpy(float), status=np.asarray(events, int),
              ties="breslow").fit()
    bh = m.baseline_cumulative_hazard[0]
    return CoxPH(np.asarray(m.params), np.asarray(m.bse), cols, np.asarray(bh[0]), np.asarray(bh[1]))


# ---------------------------------------------------------------- term structure
def term_structure(cum_pd_monthly: np.ndarray, years: int = 5) -> pd.DataFrame:
    """Converte curva de PD acumulada mensal em PD acumulada/marginal por ano
    e PD condicional (hazard anual)."""
    cum = np.asarray(cum_pd_monthly, dtype=float)
    rows, prev = [], 0.0
    for y in range(1, years + 1):
        m = min(12 * y, len(cum)) - 1
        c = float(cum[m])
        marginal = c - prev
        rows.append({"year": y, "cumulative_pd": c, "marginal_pd": marginal,
                     "conditional_pd": marginal / (1 - prev) if prev < 1 else np.nan})
        prev = c
    return pd.DataFrame(rows)


def simple_lifetime_pd(pd_12m: float, months) -> np.ndarray:
    """Aproximação da v2: hazard constante, PD_lifetime = 1 − (1 − PD12)^(T/12)."""
    return 1 - (1 - pd_12m) ** (np.asarray(months, dtype=float) / 12)
