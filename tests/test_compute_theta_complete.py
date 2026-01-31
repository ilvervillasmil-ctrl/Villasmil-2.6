from villasmil_omega.core import compute_theta


def test_compute_theta_all_branches():
    # Rama 1: cluster vacío
    assert compute_theta([]) == 0.0

    # Rama 3: cluster no vacío, pero sin contradicción suficiente
    low_tension_cluster = [
        "model a explains behavior",
        "model a is consistent",
        "model a prediction",
    ]
    assert compute_theta(low_tension_cluster) == 0.0

    # Rama 2: cluster largo con contradicción activa
    high_tension_cluster = [
        "model a explains behavior",
        "model a is consistent",
        "model a prediction",
        "model b explains behavior",
        "model b is consistent",
        "model b prediction",
    ]
    assert compute_theta(high_tension_cluster) == 1.0
