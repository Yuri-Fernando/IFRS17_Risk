"""
Modelagem de EAD (Exposure at Default).

Para produtos com desembolso integral na concessão (o caso do dataset —
empréstimos parcelados de prazo fixo), a EAD é aproximada pelo saldo
devedor no momento da avaliação, aplicando um Credit Conversion Factor
(CCF) sobre a parcela ainda não amortizada. Para simplificação do PoC,
assume-se amortização linear (SAC-like) ao longo do prazo contratual —
premissa documentada em `reports/assumptions.md` — e um CCF=1 (produto
100% desembolsado, sem limite rotativo a converter, diferente de cartão de
crédito/cheque especial).
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def estimate_ead(df: pd.DataFrame, elapsed_fraction: float = 0.3, ccf: float = 1.0) -> np.ndarray:
    """Calcula a EAD de cada contrato.

    Parameters
    ----------
    elapsed_fraction: fração do prazo já decorrida na data-base (assume-se
        0.3 — carteira "em curso" — na ausência de data de originação real
        no dataset).
    ccf: Credit Conversion Factor aplicado ao saldo remanescente.
    """
    remaining_fraction = np.clip(1 - elapsed_fraction, 0.0, 1.0)
    outstanding_balance = df["exposure_amount"].values * remaining_fraction
    return outstanding_balance * ccf
