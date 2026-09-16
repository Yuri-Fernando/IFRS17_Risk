"""
Motor de Experiência (A/E Ratio) — compara sinistros observados vs. esperados
pela tábua biométrica, por célula de risco (idade x sexo x produto x mês).

Reproduz a lógica de conciliação em 3 categorias (oficial / sensibilidade /
pendente) documentada em itau/METODOLOGIA_MESTRE.md, seção 2 (Fase 6) e 3.2 —
aqui aplicada sobre dados 100% sintéticos.
"""
from __future__ import annotations

import numpy as np
import pandas as pd

from src.data.mortality_tables import qx_base_table


def age_band(age: pd.Series, width: int = 5) -> pd.Series:
    return (age // width * width).astype(int)


def expected_events_by_cell(
    exposure: pd.DataFrame,
    age_band_width: int = 5,
) -> pd.DataFrame:
    """Calcula eventos esperados = expostos x qx(idade), agregados por célula
    (faixa etária x sexo x produto x ano-mês)."""
    df = exposure.copy()
    df["age_band"] = age_band(df["age"], age_band_width)
    df["year_month"] = pd.to_datetime(df["year_month"])

    qx_male = qx_base_table("male")
    qx_female = qx_base_table("female")
    df["qx"] = np.where(df["sex"] == "male", qx_male(df["age"]), qx_female(df["age"]))
    df["expected_events"] = df["qx"] / 12.0  # qx anual -> incidência mensal

    grouped = (
        df.groupby(["age_band", "sex", "product", "year_month"], observed=True)
        .agg(
            n_exposed=("policy_id", "count"),
            expected_events=("expected_events", "sum"),
            total_contribution=("contribution", "sum"),
        )
        .reset_index()
    )
    return grouped


def reconcile_claims(
    claims: pd.DataFrame,
    exposure: pd.DataFrame,
    age_band_width: int = 5,
) -> pd.DataFrame:
    """Concilia sinistros com a base de exposição por chave (faixa etária x
    sexo x produto x mês). Classifica em oficial (match no mesmo mês) e
    sensibilidade (match no mês anterior, por causa do lag de aviso) — espelha
    a lógica real descrita na metodologia."""
    c = claims.copy()
    c["occurrence_month"] = pd.to_datetime(c["occurrence_month"])
    c["age_band"] = age_band(c["age_at_event"], age_band_width)
    c["key_month"] = c["occurrence_month"]

    valid_keys = set(
        zip(
            exposure["age_band"] if "age_band" in exposure.columns else age_band(exposure["age"], age_band_width),
            exposure["sex"],
            exposure["product"],
            pd.to_datetime(exposure["year_month"]),
        )
    )

    def classify(row):
        key_official = (row["age_band"], row["sex"], row["product"], row["key_month"])
        if key_official in valid_keys:
            return "oficial"
        key_prev_month = row["key_month"] - pd.offsets.MonthBegin(1)
        key_sensitivity = (row["age_band"], row["sex"], row["product"], key_prev_month)
        if key_sensitivity in valid_keys:
            return "sensibilidade"
        return "pendente"

    c["reconciliation_status"] = c.apply(classify, axis=1)
    return c


def ae_ratio_by_cell(
    exposure: pd.DataFrame,
    claims: pd.DataFrame,
    age_band_width: int = 5,
    include_status: tuple[str, ...] = ("oficial",),
) -> pd.DataFrame:
    """Junta esperado (da exposição) com observado (dos sinistros conciliados)
    por célula e calcula o A/E ratio."""
    expected = expected_events_by_cell(exposure, age_band_width)
    reconciled = reconcile_claims(claims, exposure, age_band_width)
    reconciled = reconciled[reconciled["reconciliation_status"].isin(include_status)]

    observed = (
        reconciled.assign(year_month=reconciled["occurrence_month"])
        .groupby(["age_band", "sex", "product", "year_month"], observed=True)
        .size()
        .rename("observed_events")
        .reset_index()
    )

    merged = expected.merge(observed, on=["age_band", "sex", "product", "year_month"], how="left")
    merged["observed_events"] = merged["observed_events"].fillna(0)
    merged["ae_ratio"] = np.where(
        merged["expected_events"] > 0,
        merged["observed_events"] / merged["expected_events"],
        np.nan,
    )
    return merged


def ae_ratio_summary(cell_df: pd.DataFrame, group_cols: list[str] | None = None) -> pd.DataFrame:
    """Agrega o A/E ratio por produto (ou outra dimensão) somando observado e
    esperado antes de dividir — evita o viés de fazer média de razões."""
    group_cols = group_cols or ["product"]
    summary = (
        cell_df.groupby(group_cols, observed=True)
        .agg(observed_events=("observed_events", "sum"), expected_events=("expected_events", "sum"))
        .reset_index()
    )
    summary["ae_ratio"] = summary["observed_events"] / summary["expected_events"]
    return summary


def monthly_loss_ratio_series(exposure: pd.DataFrame, claims: pd.DataFrame) -> pd.DataFrame:
    """Constrói a série mensal de sinistralidade = sinistro pago / contribuição
    arrecadada — a métrica usada como insumo da simulação de Monte Carlo
    (ver src/simulation/monte_carlo.py), replicando a lógica real do projeto."""
    exposure = exposure.copy()
    exposure["year_month"] = pd.to_datetime(exposure["year_month"])
    premium = exposure.groupby("year_month")["contribution"].sum().rename("total_premium")

    claims = claims.copy()
    claims["occurrence_month"] = pd.to_datetime(claims["occurrence_month"])
    paid = claims.groupby("occurrence_month")["benefit_reference"].sum().rename("total_paid")

    series = pd.concat([premium, paid], axis=1).fillna(0.0).sort_index()
    series["loss_ratio"] = np.where(series["total_premium"] > 0, series["total_paid"] / series["total_premium"], 0.0)
    return series.reset_index().rename(columns={"index": "year_month"})
