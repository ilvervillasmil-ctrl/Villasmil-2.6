from villasmil_omega.core import run_core, indice_mc


def test_run_core_executes_without_error(capsys):
    # Solo comprobamos que imprime algo y no lanza excepciones
    run_core()
    captured = capsys.readouterr()
    assert "Villasmil-Ω v2.6 Core Module" in captured.out


def test_indice_mc_non_trivial_case():
    # Caso con aciertos y errores para cubrir la rama total != 0
    score = indice_mc(aciertos=3, errores=1)
    assert 0 < score <= 1
    assert score == 3 / 4
