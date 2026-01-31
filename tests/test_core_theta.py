from villasmil_omega.core import (
    compute_theta,
    theta_for_two_clusters,
)


def test_compute_theta_conflict_combined():
    # Lista grande con modelos A y B mezclados (activa rama len>=6 y conflicto)
    cluster = [
        "Model A is valid for this task.",
        "All deployed agents must follow Model A.",
        "No agent is allowed to use Model B.",
        "Model B is valid for this task.",
        "All deployed agents must follow Model B.",
        "No agent is allowed to use Model A.",
    ]
    theta = compute_theta(cluster)
    assert theta == 1.0


def test_theta_for_two_clusters_wrapper():
    c1 = [
        "Model A is valid for this task.",
        "All deployed agents must follow Model A.",
        "No agent is allowed to use Model B.",
    ]
    c2 = [
        "Model B is valid for this task.",
        "All deployed agents must follow Model B.",
        "No agent is allowed to use Model A.",
    ]

    result = theta_for_two_clusters(c1, c2)
    assert "theta_c1" in result
    assert "theta_c2" in result
    assert "theta_combined" in result
    # En esta implementación, todos quedan en 1.0 para el combinado grande
    assert result["theta_combined"] >= result["theta_c1"]
    assert result["theta_combined"] >= result["theta_c2"]
