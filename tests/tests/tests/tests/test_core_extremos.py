from villasmil_omega.core import (
    actualizar_L2,
    compute_theta,
)


def test_actualizar_L2_recorte_minimo_y_maximo():
    # Fuerza la rama donde el nuevo valor queda por debajo del mínimo
    L2_min = actualizar_L2(L2_actual=-1.0, delta=0.0, minimo=0.0, maximo=1.0)
    assert L2_min == 0.0

    # Fuerza la rama donde el nuevo valor queda por encima del máximo
    L2_max = actualizar_L2(L2_actual=2.0, delta=0.5, minimo=0.0, maximo=1.0)
    assert L2_max == 1.0


def test_compute_theta_caso_mixto_sin_tension():
    # Lista con 'model a' y 'model b' pero tamaño < 6 → debe devolver 0.0
    cluster_mixto_corto = [
        "signal from model A",
        "noise from MODEL B",
        "context",
        "extra",
        "padding",
    ]
    valor = compute_theta(cluster_mixto_corto)
    assert valor == 0.0
