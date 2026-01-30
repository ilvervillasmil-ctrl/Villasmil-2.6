from villasmil_omega.core import (
    run_core,
    suma_omega,
    indice_mc,
    indice_ci,
    actualizar_L2,
    penalizar_MC_CI,
)


def test_run_core_prints_banner(capsys):
    run_core()
    captured = capsys.readouterr()
    assert "Villasmil-Ω v2.6 Core Module" in captured.out
    assert "Author: Ilver Villasmil" in captured.out
    assert "Module loaded successfully" in captured.out


def test_suma_omega_basic():
    assert suma_omega(2, 3) == 5
    assert suma_omega(-1, 1) == 0


def test_indice_mc_normal_case():
    score = indice_mc(aciertos=3, errores=1)
    assert score == 3 / 4


def test_indice_mc_zero_total():
    score = indice_mc(aciertos=0, errores=0)
    assert score == 0.0


def test_indice_ci_normal_case():
    score = indice_ci(aciertos=4, errores=1, ruido=1)
    assert 0.0 < score <= 1.0


def test_indice_ci_zero_total():
    score = indice_ci(aciertos=0, errores=0, ruido=0)
    assert score == 0.0


def test_actualizar_L2_towards_optimum():
    start = 0.5
    new = actualizar_L2(L2_actual=start, k=0.25, L2_opt=0.125)
    # Debe moverse hacia 0.125 y alejarse de 0.5
    assert new < start
    assert new > 0.125


def test_penalizar_MC_CI_penalizes_when_L2_off():
    MC_pen, CI_pen = penalizar_MC_CI(MC=1.0, CI=1.0, L2=0.5, L2_opt=0.125)
    assert MC_pen < 1.0
    assert CI_pen < 1.0


def test_penalizar_MC_CI_no_penalty_when_optimal():
    MC_pen, CI_pen = penalizar_MC_CI(MC=0.8, CI=0.6, L2=0.125, L2_opt=0.125)
    assert MC_pen == 0.8
    assert CI_pen == 0.6
