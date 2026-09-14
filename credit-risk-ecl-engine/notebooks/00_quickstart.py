# %% [markdown]
# # Credit Risk ECL Engine — Quickstart
#
# Script no formato "percent" (compatível com Jupytext / VS Code
# interactive window — cada `# %%` é uma célula). Abra no Jupyter via
# `jupyter notebook` + Jupytext, ou rode direto como script Python.

# %%
import sys
from pathlib import Path

sys.path.insert(0, str(Path.cwd().parent if Path.cwd().name == "notebooks" else Path.cwd()))

from src.cloud.pipeline import run_pipeline

# %% [markdown]
# ## 1. Executa o pipeline completo com o dataset real (German Credit)

# %%
result = run_pipeline(
    data_source="csv",
    data_path="data/raw/german_credit.csv",
    n_simulations=10000,
    inter_segment_correlation=0.25,
    asset_correlation=0.15,
    verbose=True,
)

# %% [markdown]
# ## 2. Resultados principais

# %%
print(f"Modelo campeão: {result['pd_models']['champion']}")
print(f"Gini: {result['validation']['gini']:.3f} | KS: {result['validation']['ks']:.3f}")
print(f"ECL total: R$ {result['portfolio']['total_ecl']:,.2f}")
print(f"Coverage ratio: {result['portfolio']['coverage_ratio']:.2%}")
print(f"VaR 99.9%: R$ {result['monte_carlo']['var']['var_99.9']:,.2f}")

# %% [markdown]
# ## 3. ECL por stage (tabela)

# %%
import pandas as pd

pd.DataFrame(result["ecl_by_stage"])

# %% [markdown]
# ## 4. Distribuição de perdas simuladas (histograma)

# %%
import matplotlib.pyplot as plt

df_ecl = result["df_ecl"]

# %% [markdown]
# ## 5. Stress testing — sensibilidade da provisão

# %%
pd.DataFrame(result["stress_test"])[["label", "total_ecl", "ecl_delta_pct"]]

# %% [markdown]
# ## 6. Exportar carteira detalhada por contrato

# %%
df_ecl.to_csv("data/processed/portfolio_ecl_scored.csv", index=False)
print("Exportado em data/processed/portfolio_ecl_scored.csv")
