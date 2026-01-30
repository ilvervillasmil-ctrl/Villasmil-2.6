from villasmil_omega.core import (
    indice_mc,
    indice_ci,
    actualizar_L2,
    penalizar_MC_CI,
)


def test_indice_mc_total_zero():
    assert indice_mc(0, 0) == 0.0


def test_indice_ci_total_zero():
    assert indice_ci(0, 0, 0) == 0.0


def test_actualizar_L2_basico():
    L2_actual = 0.0
    nuevo = actualizar_L2(L2_actual)
    assert nuevo != L2_actual


def test_penalizar_MC_CI_basico():
    MC, CI = 1.0, 1.0
    MC_p, CI_p = penalizar_MC_CI(MC, CI, L2=0.0)
    assert MC_p <= MC
    assert CI_p <= CI

