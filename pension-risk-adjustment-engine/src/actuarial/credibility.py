"""
Credibility Testing (Bühlmann) — item identificado na metodologia original
(itau/METODOLOGIA_MESTRE.md, seções 3.3 e 6, gap #8) mas nunca implementado em
código durante o projeto real. Implementado aqui como parte das melhorias
propostas (seção 8, item 1).

Lógica: quando uma célula de risco (idade x sexo x produto) tem exposição
insuficiente para que o A/E observado seja estatisticamente confiável, o fator
final é uma média ponderada entre o A/E observado e o benchmark de mercado
(A/E = 1.0, ou seja, a própria tábua), com peso Z crescente conforme a
exposição e o número de eventos aumentam.
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def buhlmann_credibility_factor(
    n_exposed: float,
    n_events: float,
    full_credibility_exposure: float = 1000.0,
    full_credibility_events: float = 30.0,
) -> float:
    """Fator de credibilidade Z em [0, 1], usando a regra clássica do "método
    do limite de flutuação" (Bühlmann/Limited Fluctuation Credibility):
    Z = sqrt(min(exposição/exposição_plena, eventos/eventos_plenos, 1)).

    Isso implementa a fórmula geral fator = Z * AE_interno + (1-Z) * AE_mercado
    descrita na metodologia (AE_mercado = 1.0, isto é, a tábua base sem ajuste).
    """
    if full_credibility_exposure <= 0 or full_credibility_events <= 0:
        raise ValueError("os parâmetros de credibilidade plena devem ser positivos")

    z_exposure = min(n_exposed / full_credibility_exposure, 1.0)
    z_events = min(n_events / full_credibility_events, 1.0)
    z = np.sqrt(min(z_exposure, z_events))
    return float(np.clip(z, 0.0, 1.0))


def apply_credibility(
    cell_df: pd.DataFrame,
    full_credibility_exposure: float = 1000.0,
    full_credibility_events: float = 30.0,
    market_ae: float = 1.0,
) -> pd.DataFrame:
    """Aplica o fator de credibilidade célula a célula, produzindo um A/E
    ajustado que blenda o observado com o benchmark de mercado quando a
    exposição da célula é pequena."""
    out = cell_df.copy()
    out["credibility_z"] = out.apply(
        lambda r: buhlmann_credibility_factor(
            r["n_exposed"], r["observed_events"], full_credibility_exposure, full_credibility_events
        ),
        axis=1,
    )
    out["ae_ratio_raw"] = out["ae_ratio"]
    out["ae_ratio_credibility_adjusted"] = (
        out["credibility_z"] * out["ae_ratio_raw"].fillna(market_ae) + (1 - out["credibility_z"]) * market_ae
    )
    return out
