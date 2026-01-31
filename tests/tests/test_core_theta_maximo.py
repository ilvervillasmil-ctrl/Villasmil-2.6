from villasmil_omega.core import compute_theta


def test_compute_theta_tension_alta():
    # Lista con al menos 6 elementos, conteniendo 'model a' y 'model b'
    cluster_largo_mixto = [
        "first signal from model A",
        "second signal from model B",
        "context 1",
        "context 2",
        "more noise",
        "extra padding element",
    ]
    valor = compute_theta(cluster_largo_mixto)
    assert valor == 1.0

