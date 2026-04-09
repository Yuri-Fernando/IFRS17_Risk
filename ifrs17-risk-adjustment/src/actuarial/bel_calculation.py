"""Cálculo de BEL (Best Estimate Liability)."""

import pandas as pd
import numpy as np


def calculate_bel(projections, discount_rate=0.05, risk_profile='medium'):
    """Calcula BEL a partir de projeções de fluxos."""
    # Converte para DataFrame
    if isinstance(projections, dict):
        data = []
        for year, cf in projections.items():
            data.append({
                'year': cf.get('year', year),
                'total_premium': cf.get('total_premium', 0),
                'total_claims': cf.get('total_claims', 0),
                'total_expenses': cf.get('total_expenses', 0),
            })
        df = pd.DataFrame(data)
    else:
        df = projections.copy()

    # Cálculo de Valor Presente
    df['pv_factor'] = 1 / ((1 + discount_rate) ** df['year'])
    pv_premiums = (df['total_premium'] * df['pv_factor']).sum()
    pv_claims = (df['total_claims'] * df['pv_factor']).sum()
    pv_expenses = (df['total_expenses'] * df['pv_factor']).sum()

    bel_base = pv_premiums - pv_claims - pv_expenses
    
    risk_adj = {'low': 0.95, 'medium': 1.00, 'high': 1.05}
    adjustment = risk_adj.get(risk_profile, 1.00)
    bel_adjusted = bel_base * adjustment

    return {
        'pv_premiums': pv_premiums,
        'pv_claims': pv_claims,
        'pv_expenses': pv_expenses,
        'bel_base': bel_base,
        'total_bel': bel_adjusted,
        'discount_rate': discount_rate,
    }


def validate_bel(bel):
    """Valida se o BEL é razoável."""
    total_bel = bel.get('total_bel', 0)
    pv_premiums = bel.get('pv_premiums', 1)
    pv_claims = bel.get('pv_claims', 0)

    if total_bel <= 0:
        return False
    if total_bel > pv_premiums:
        return False
    if pv_premiums > 0:
        loss_ratio = pv_claims / pv_premiums
        if loss_ratio < 0 or loss_ratio > 1.5:
            return False
    return True
