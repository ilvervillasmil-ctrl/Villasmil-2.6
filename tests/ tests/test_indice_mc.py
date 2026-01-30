from villasmil_omega.core import indice_mc


def test_indice_mc_varios_casos():
    # Caso normal: 8 de 10
    assert indice_mc(8, 2) == 0.8

    # Caso perfecto: 10 de 10
    assert indice_mc(10, 0) == 1.0

    # Caso cero aciertos: 0 de 5
    assert indice_mc(0, 5) == 0.0

    # Caso borde: nadie respondió (0, 0) -> 0.0
    assert indice_mc(0, 0) == 0.0

