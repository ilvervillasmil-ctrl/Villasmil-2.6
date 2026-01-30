# tests/test_compute_theta_no_conflict.py

from villasmil_omega.core import compute_theta  # o computetheta, ajusta al nombre real


def test_compute_theta_no_conflict_all_compatible():
    """
    Si todas las premisas son compatibles entre sí, Θ(C) debe ser 0.0.
    Caso base: el sistema no debe inventar conflicto donde no lo hay.
    """
    premises = [
        {"id": 1, "constraints": {"A": True}},
        {"id": 2, "constraints": {"B": True}},
        {"id": 3, "constraints": {"C": True}},
    ]

    theta = compute_theta(premises)

    assert theta == 0.0
