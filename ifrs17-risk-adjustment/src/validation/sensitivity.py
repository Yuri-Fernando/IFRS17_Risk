"""Análise de sensibilidade."""

import numpy as np


def one_way_sensitivity(base_value, parameter_name, variations):
    """Sensibilidade unidirecional."""
    results = {}
    for variation in variations:
        results[f'{parameter_name}_{variation}'] = base_value * variation
    return results


def two_way_sensitivity(base_value, param1, param2, variations):
    """Sensibilidade bidirecional."""
    return {'two_way': 'analysis'}


def tornado_analysis(base_value, parameters):
    """Tornado analysis."""
    return {'tornado': 'analysis', 'parameters': parameters}


def elasticity_analysis(base_value, parameters):
    """Análise de elasticidade."""
    return {'elasticity': 'analysis'}


def sensitivity_analysis(model, parameters, ranges):
    """Sensibilidade geral."""
    return {'sensitivity': 'analysis'}
