"""
Cálculo de ECL (Expected Credit Loss) — IFRS 9 §5.5 / Resolução CMN 4.966.

    ECL_Stage1 = PD_12m       x LGD x EAD
    ECL_Stage2 = PD_lifetime  x LGD x EAD
    ECL_Stage3 = PD_lifetime  x LGD x EAD   (PD_lifetime = 100%)

A provisão total da carteira é a soma da ECL de todos os contratos,
segmentada por stage — exatamente como exigido na nota explicativa de
risco de crédito das demonstrações financeiras.
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def calculate_ecl(df: pd.DataFrame, lgd: np.ndarray, ead: np.ndarray) -> pd.DataFrame:
    out = df.copy()
    out["lgd"] = lgd
    out["ead"] = ead

    pd_used = np.where(out["stage"].values == 1, out["pd_12m"].values, out["pd_lifetime"].values)
    out["pd_used"] = pd_used
    out["ecl"] = out["pd_used"] * out["lgd"] * out["ead"]
    return out


def summarize_ecl_by_stage(df_ecl: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df_ecl.groupby("stage")
        .agg(
            n_contracts=("contract_id", "count"),
            total_exposure=("ead", "sum"),
            avg_pd=("pd_used", "mean"),
            avg_lgd=("lgd", "mean"),
            total_ecl=("ecl", "sum"),
        )
        .reset_index()
    )
    summary["coverage_ratio"] = summary["total_ecl"] / summary["total_exposure"]
    return summary


def summarize_ecl_by_segment(df_ecl: pd.DataFrame) -> pd.DataFrame:
    summary = (
        df_ecl.groupby("segment")
        .agg(
            n_contracts=("contract_id", "count"),
            total_exposure=("ead", "sum"),
            total_ecl=("ecl", "sum"),
        )
        .reset_index()
    )
    summary["coverage_ratio"] = summary["total_ecl"] / summary["total_exposure"]
    return summary


def portfolio_totals(df_ecl: pd.DataFrame) -> dict:
    return {
        "n_contracts": int(len(df_ecl)),
        "total_exposure": float(df_ecl["ead"].sum()),
        "total_ecl": float(df_ecl["ecl"].sum()),
        "coverage_ratio": float(df_ecl["ecl"].sum() / df_ecl["ead"].sum()),
        "n_stage1": int((df_ecl["stage"] == 1).sum()),
        "n_stage2": int((df_ecl["stage"] == 2).sum()),
        "n_stage3": int((df_ecl["stage"] == 3).sum()),
    }
