import villasmil_omega
from villasmil_omega.core import (
    suma_omega,
    indice_mc,
    indice_ci,
)


def test_package_init_imports():
    assert villasmil_omega is not None


def test_suma_omega_normal_case():
    assert suma_omega(2, 3) == 5


def test_indice_mc_normal_case():
    assert indice_mc(3, 1) == 3 / 4


def test_indice_ci_normal_case():
    valor = indice_ci(aciertos=3, errores=1, ruido=0)
    assert 0.0 <= valor <= 1.0
