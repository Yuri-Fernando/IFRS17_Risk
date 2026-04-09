"""
Projeção de Fluxos de Caixa

Simula fluxos futuros de caixa em portfólio atuarial.
Essencial para cálculo de BEL (Best Estimate Liability) sob IFRS 17.

Fluxos incluem:
- Prêmios futuros
- Benefícios (sinistros, pagamentos)
- Cancelamentos (lapse)
- Despesas
"""

import pandas as pd
import numpy as np


def project_cashflows(
    data: pd.DataFrame,
    projection_years: int = 30,
    premium_inflation: float = 0.02,
    expense_ratio: float = 0.10
) -> dict:
    """
    Projeta fluxos de caixa de forma genérica.

    Metodologia:
    - Usa dados disponíveis no dataset
    - Projeta receitas/despesas com inflação
    - Estima sinistralidade baseada em dados históricos

    Args:
        data: DataFrame com dados de contratos
        projection_years: anos de projeção
        premium_inflation: taxa anual de inflação
        expense_ratio: percentual de despesas

    Returns:
        Dicionário com projeções por ano
    """
    projections = {}

    # Cálculos agregados do dataset
    n_records = len(data)

    # Detecta coluna de sinistros
    claim_col = None
    if 'claim_status' in data.columns:
        claim_col = 'claim_status'
    elif 'claim' in data.columns:
        claim_col = 'claim'
    else:
        # Se não houver coluna de sinistros, usa a primeira coluna numérica
        numeric_cols = data.select_dtypes(include=[np.number]).columns
        claim_col = numeric_cols[0] if len(numeric_cols) > 0 else None

    # Taxa de sinistralidade observada
    sinistralidade = data[claim_col].mean() if claim_col else 0.15

    # Média de valores (usa qualquer coluna numérica disponível)
    numeric_cols = data.select_dtypes(include=[np.number]).columns.tolist()
    valor_medio = data[numeric_cols].mean().mean() if numeric_cols else 1000

    # Base de receita inicial (prêmios agregados)
    receita_base = n_records * valor_medio * 0.5

    for year in range(1, projection_years + 1):
        year_cf = {
            'year': year,
            'total_premium': 0,
            'total_claims': 0,
            'total_lapse': 0,
            'total_expenses': 0,
            'net_cashflow': 0
        }

        # Prêmios com inflação
        total_premium = receita_base * ((1 + premium_inflation) ** year)

        # Sinistros esperados (baseado em sinistralidade observada)
        total_claims = total_premium * sinistralidade * 0.8  # 80% da sinistralidade

        # Lapse (cancelamento) - aumenta gradualmente com tempo
        lapse_rate = 0.05 * (1 + 0.02 * year)  # 5% base + crescimento
        total_lapse = total_premium * lapse_rate

        # Despesas
        total_expenses = total_premium * expense_ratio

        # Fluxo líquido
        net_cashflow = total_premium - total_claims - total_lapse - total_expenses

        year_cf['total_premium'] = total_premium
        year_cf['total_claims'] = total_claims
        year_cf['total_lapse'] = total_lapse
        year_cf['total_expenses'] = total_expenses
        year_cf['net_cashflow'] = net_cashflow

        projections[year] = year_cf

    return projections


def get_cashflow_summary(projections: dict) -> pd.DataFrame:
    """
    Converte projeções em DataFrame para visualização.

    Args:
        projections: Dicionário de projeções por ano

    Returns:
        DataFrame com resumo dos fluxos por ano
    """
    data = []

    for year, cf in projections.items():
        data.append({
            'year': cf['year'],
            'total_premium': cf['total_premium'],
            'total_claims': cf['total_claims'],
            'total_lapse': cf['total_lapse'],
            'total_expenses': cf['total_expenses'],
            'net_cashflow': cf['net_cashflow']
        })

    df = pd.DataFrame(data)
    return df


def calculate_bel_simple(projections: dict, discount_rate: float = 0.05) -> dict:
    """
    Calcula BEL simples como valor presente dos fluxos.

    Args:
        projections: Dicionário de projeções
        discount_rate: Taxa de desconto

    Returns:
        Dicionário com BEL por componente
    """
    summary = get_cashflow_summary(projections)

    # Desconta fluxos para valor presente
    pv_premiums = (summary['total_premium'] / ((1 + discount_rate) ** summary['year'])).sum()
    pv_claims = (summary['total_claims'] / ((1 + discount_rate) ** summary['year'])).sum()
    pv_expenses = (summary['total_expenses'] / ((1 + discount_rate) ** summary['year'])).sum()

    bel = {
        'pv_premiums': pv_premiums,
        'pv_claims': pv_claims,
        'pv_expenses': pv_expenses,
        'total_bel': pv_premiums - pv_claims - pv_expenses
    }

    return bel
