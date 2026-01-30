"""
Edge-case coverage tests for Villasmil-Ω v2.6
Objetivo: cubrir ramas que faltan en core.py
"""

from villasmil_omega.core import (
    indice_mc,
    indice_ci,
    actualizar_L2,
    penalizar_MC_CI,
)


def test_indice_mc_total_zero():
    # Rama: total == 0 en indice_mc
    assert indice_mc(0, 0) == 0.0


def test_indice_ci_total_zero():
    # Rama: total == 0 en indice_ci
    assert indice_ci(0, 0, 0) == 0.0


def test_actualizar_L2_se_acerca_a_optimo():
    # Verifica que L2 se mueve hacia L2_opt
    L2_actual = 0.0
    nuevo = actualizar_L2(L2_actual, k=0.5, L2_opt=0.125)
    assert 0.0 < nuevo < 0.125


def test_penalizar_MC_CI_aplica_penalizacion():
    MC, CI = 1.0, 1.0
    # Usamos L2 lejos del óptimo para forzar penalización
    MC_p, CI_p = penalizar_MC_CI(MC, CI, L2=0.0, L2_opt=0.125, alpha=0.5, beta=0.5)
    assert MC_p < MC
    assert CI_p < CI
