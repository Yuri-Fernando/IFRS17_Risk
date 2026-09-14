"""
Carregamento de dados de carteira de crédito.

Fonte real usada no PoC: UCI Statlog German Credit Data (1000 contratos,
20 variáveis + flag de inadimplência), amplamente usado como benchmark
acadêmico para modelos de PD / credit scoring.

Referência: Hofmann, H. (1994). Statlog (German Credit Data). UCI Machine
Learning Repository. https://archive.ics.uci.edu/dataset/144
Espelho estruturado (com nomes de coluna legíveis) usado aqui:
https://raw.githubusercontent.com/selva86/datasets/master/GermanCredit.csv

Também oferece geração de dados sintéticos (fallback) para permitir rodar
o pipeline sem dependência de internet, mantendo a mesma interface.
"""

from __future__ import annotations

import numpy as np
import pandas as pd

RAW_COLUMNS_TARGET = "credit_risk"  # 1 = bom pagador, 0 = inadimplente (dataset original)
TARGET_COLUMN = "default"  # 1 = default/inadimplente, 0 = performing (convenção deste projeto)


def load_german_credit(path: str) -> pd.DataFrame:
    """Carrega o dataset German Credit e normaliza o target.

    No arquivo original, `credit_risk == 1` significa "bom pagador".
    Neste projeto invertemos a semântica para `default == 1` (convenção
    de risco de crédito / PD), que é o padrão usado em modelagem de ECL.
    """
    df = pd.read_csv(path)

    if RAW_COLUMNS_TARGET not in df.columns:
        raise ValueError(
            f"Coluna alvo '{RAW_COLUMNS_TARGET}' não encontrada em {path}. "
            "Verifique se o dataset baixado é o German Credit (selva86/UCI)."
        )

    df = df.rename(columns={"amount": "exposure_amount", "duration": "term_months"})
    df[TARGET_COLUMN] = 1 - df[RAW_COLUMNS_TARGET]
    df = df.drop(columns=[RAW_COLUMNS_TARGET])

    # Identificador de contrato — necessário para trilha de auditoria e joins
    df.insert(0, "contract_id", [f"CR{i:05d}" for i in range(1, len(df) + 1)])
    return df


def generate_synthetic_portfolio(n: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Gera uma carteira sintética com a mesma estrutura de colunas do
    German Credit, para permitir execução do pipeline sem internet
    (`--data-source synthetic`).
    """
    rng = np.random.default_rng(seed)

    status_opts = [
        "no checking account",
        "... < 0 DM",
        "0 <= ... < 200 DM",
        "... >= 200 DM / salary assignments for at least 1 year",
    ]
    purpose_opts = [
        "domestic appliances",
        "car (new)",
        "car (used)",
        "furniture/equipment",
        "radio/television",
        "business",
        "education",
    ]
    property_opts = ["real estate", "building society savings/life insurance", "car or other", "unknown/no property"]
    job_opts = ["unskilled - resident", "skilled employee/official", "management/self-employed/highly qualified"]

    term_months = rng.choice([6, 12, 18, 24, 36, 48, 60], size=n)
    exposure_amount = np.round(rng.lognormal(mean=8.2, sigma=0.7, size=n)).astype(int)
    age = rng.integers(19, 76, size=n)
    installment_rate = rng.integers(1, 5, size=n)
    number_credits = rng.integers(1, 4, size=n)
    people_liable = rng.integers(1, 3, size=n)

    status = rng.choice(status_opts, size=n, p=[0.35, 0.25, 0.25, 0.15])
    purpose = rng.choice(purpose_opts, size=n)
    property_ = rng.choice(property_opts, size=n)
    job = rng.choice(job_opts, size=n, p=[0.2, 0.6, 0.2])

    # Probabilidade latente de default correlacionada com risco observável,
    # para que os modelos treinados no sintético também façam sentido.
    risk_score = (
        0.55 * (status == "no checking account").astype(float) * -1
        + 0.35 * (exposure_amount / exposure_amount.max())
        + 0.25 * (term_months / term_months.max())
        - 0.20 * (age / age.max())
        + rng.normal(0, 0.15, size=n)
    )
    pd_latent = 1 / (1 + np.exp(-(risk_score - risk_score.mean()) * 3))
    default = (rng.uniform(size=n) < pd_latent * 0.4).astype(int)  # ~taxa de inadimplência plausível

    df = pd.DataFrame(
        {
            "contract_id": [f"SYN{i:05d}" for i in range(1, n + 1)],
            "status": status,
            "term_months": term_months,
            "credit_history": rng.choice(
                ["critical account/other credits existing", "existing credits paid back duly till now", "no credits taken/all credits paid back duly"],
                size=n,
            ),
            "purpose": purpose,
            "exposure_amount": exposure_amount,
            "savings": rng.choice(["... < 100 DM", "100 <= ... < 500 DM", "unknown/no savings account", "... >= 1000 DM"], size=n),
            "employment_duration": rng.choice(["unemployed", "... < 1 year", "1 <= ... < 4 years", "... >= 7 years"], size=n),
            "installment_rate": installment_rate,
            "personal_status_sex": rng.choice(["male : single", "female : divorced/separated/married", "male : married/widowed"], size=n),
            "other_debtors": rng.choice(["none", "co-applicant", "guarantor"], size=n, p=[0.85, 0.1, 0.05]),
            "present_residence": rng.integers(1, 5, size=n),
            "property": property_,
            "age": age,
            "other_installment_plans": rng.choice(["none", "bank", "stores"], size=n, p=[0.8, 0.15, 0.05]),
            "housing": rng.choice(["own", "rent", "for free"], size=n, p=[0.6, 0.3, 0.1]),
            "number_credits": number_credits,
            "job": job,
            "people_liable": people_liable,
            "telephone": rng.choice(["yes", "no"], size=n),
            "foreign_worker": rng.choice(["yes", "no"], size=n, p=[0.9, 0.1]),
            TARGET_COLUMN: default,
        }
    )
    return df


def load_portfolio(source: str = "csv", path: str | None = None, n_synthetic: int = 1000, seed: int = 42) -> pd.DataFrame:
    """Ponto único de entrada de dados do pipeline.

    Parameters
    ----------
    source: 'csv' (dataset real German Credit) ou 'synthetic'
    """
    if source == "synthetic":
        return generate_synthetic_portfolio(n=n_synthetic, seed=seed)
    if source == "csv":
        if path is None:
            raise ValueError("`path` é obrigatório quando source='csv'")
        return load_german_credit(path)
    raise ValueError(f"Fonte de dados desconhecida: {source}")
