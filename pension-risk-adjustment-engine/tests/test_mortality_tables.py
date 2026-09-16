import numpy as np
import pytest

from src.data.mortality_tables import qx_base_table, qx_annuitant_table, invalidity_incidence_table


def test_qx_increases_with_age():
    qx = qx_base_table("male")
    ages = np.array([30, 50, 70, 90])
    values = qx(ages)
    assert np.all(np.diff(values) > 0), "QX deve ser estritamente crescente com a idade"


def test_qx_female_lower_than_male():
    qx_m = qx_base_table("male")
    qx_f = qx_base_table("female")
    ages = np.array([30, 50, 70])
    assert np.all(qx_f(ages) < qx_m(ages)), "QX feminino deve ser sistematicamente menor que o masculino"


def test_qx_bounded_between_0_and_1():
    qx = qx_base_table("male")
    ages = np.arange(0, 111)
    values = qx(ages)
    assert np.all(values > 0) and np.all(values < 1)


def test_invalid_sex_raises():
    with pytest.raises(ValueError):
        qx_base_table("other")


def test_annuitant_table_lower_than_base():
    base = qx_base_table("male")
    annuitant = qx_annuitant_table("male")
    ages = np.array([60, 70, 80])
    assert np.all(annuitant(ages) < base(ages)), "Tábua de renda deve ter mortalidade menor que a tábua base (seleção adversa)"


def test_invalidity_incidence_positive():
    ix = invalidity_incidence_table("female")
    ages = np.array([25, 45, 65])
    values = ix(ages)
    assert np.all(values > 0) and np.all(values < 1)
