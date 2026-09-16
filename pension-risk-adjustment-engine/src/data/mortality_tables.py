"""
Tábuas biométricas paramétricas (aproximações).

IMPORTANTE — limitação declarada: as tábuas oficiais brasileiras (BR-EMS, AT-2000,
PRSSVBR/SUSEP) têm distribuição restrita (IBA/SUSEP) e não são reproduzidas aqui
linha a linha. Este módulo usa a lei de Gompertz-Makeham, forma paramétrica clássica
e amplamente aceita em literatura atuarial para aproximar a forma de uma curva de
mortalidade humana (mortalidade quase constante em idade adulta jovem + componente
exponencial dominante em idades avançadas), calibrada para produzir uma ordem de
grandeza e um formato de curva plausíveis e realistas para o mercado segurador
brasileiro — não os valores oficiais exatos tabelados.

Referência da forma funcional: Makeham, W.M. (1860); uso consolidado em modelagem
atuarial de mortalidade (ver Bowers et al., "Actuarial Mathematics").
"""
from __future__ import annotations

import numpy as np
import pandas as pd


def _makeham_qx(age: np.ndarray, a: float, b: float, c: float) -> np.ndarray:
    """qx = 1 - exp(-(A*x + B/ln(C) * (C^x - 1))) — forma de força de mortalidade
    de Makeham integrada, convertida em probabilidade anual de morte (qx)."""
    mu_integral = a * age + (b / np.log(c)) * (np.power(c, age) - 1.0)
    qx = 1.0 - np.exp(-mu_integral)
    return np.clip(qx, 1e-6, 0.999)


# Parâmetros calibrados para produzir uma curva com qx ~ 0.0005-0.001 aos 30 anos,
# ~0.01 aos 60 anos, ~0.05 aos 80 anos — ordem de grandeza plausível para tábuas
# de mercado de vida/previdência brasileiras. Feminino sistematicamente mais baixo
# que masculino, como é padrão em todas as tábuas biométricas de mercado.
_MAKEHAM_PARAMS = {
    "male": dict(a=0.0006, b=0.00004, c=1.092),
    "female": dict(a=0.0003, b=0.00002, c=1.090),
}

# Tábua de sobrevivência de renda (annuitant table): mortalidade sistematicamente
# mais baixa que a tábua de risco geral — reflete o efeito de "seleção adversa"
# (quem compra renda vitalícia tende a viver mais) observado em qualquer mercado
# de anuidades. Fator de redução aplicado sobre a tábua base.
_ANNUITANT_IMPROVEMENT_FACTOR = 0.78


def qx_base_table(sex: str) -> callable:
    """Retorna uma função qx(idade) para a tábua de mortalidade base (risco/diferimento)."""
    sex = sex.lower()
    if sex not in _MAKEHAM_PARAMS:
        raise ValueError(f"sexo inválido: {sex} (use 'male' ou 'female')")
    params = _MAKEHAM_PARAMS[sex]

    def qx(age):
        age = np.asarray(age, dtype=float)
        return _makeham_qx(age, **params)

    return qx


def qx_annuitant_table(sex: str, improvement_year_offset: int = 0, annual_improvement: float = 0.015) -> callable:
    """Tábua de renda/longevidade: mortalidade reduzida frente à tábua base, com
    trend de melhoria anual (queda de qx ao longo do tempo) parametrizável —
    replica o fenômeno documentado nas versões sucessivas das tábuas PRN/SUSEP,
    em que cada nova versão publicada reduz o qx projetado em cada idade."""
    base_qx = qx_base_table(sex)

    def qx(age):
        age = np.asarray(age, dtype=float)
        improvement = (1 - annual_improvement) ** improvement_year_offset
        return base_qx(age) * _ANNUITANT_IMPROVEMENT_FACTOR * improvement

    return qx


def build_mortality_table_df(age_min: int = 0, age_max: int = 110) -> pd.DataFrame:
    """Materializa as tábuas (base e de renda) em um DataFrame idade x sexo x tipo."""
    ages = np.arange(age_min, age_max + 1)
    rows = []
    for sex in ("male", "female"):
        qx_b = qx_base_table(sex)(ages)
        qx_a = qx_annuitant_table(sex)(ages)
        for age, qb, qa in zip(ages, qx_b, qx_a):
            rows.append({"age": age, "sex": sex, "table": "base_risk", "qx": qb})
            rows.append({"age": age, "sex": sex, "table": "annuitant", "qx": qa})
    return pd.DataFrame(rows)


def invalidity_incidence_table(sex: str) -> callable:
    """Tábua de incidência de invalidez — aproximação: fração da mortalidade base,
    crescente com a idade (padrão qualitativo de tábuas de entrada em invalidez
    tipo IAPB-57 / Álvaro Vindas, sem reproduzir seus valores exatos)."""
    base_qx = qx_base_table(sex)

    def ix(age):
        age = np.asarray(age, dtype=float)
        # fator crescente com a idade: mais incidência de invalidez em idades mais altas
        age_factor = np.clip((age - 20) / 40.0, 0.3, 2.5)
        return np.clip(base_qx(age) * 1.8 * age_factor, 1e-6, 0.2)

    return ix
