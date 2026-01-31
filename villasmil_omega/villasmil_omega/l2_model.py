"""
Modelo L2 para villasmil_omega.
"""

def compute_theta(L2, sigma=1.0):
    """
    Calcula θ(L2) = exp(−(L2 − 0.125)^2 / (2 * sigma^2))

    L2: valor del índice L2 en [0, 1].
    sigma: parámetro de dispersión (por defecto 1.0).

    Retorna un valor en (0, 1].
    """
    from math import exp

    delta = L2 - 0.125
    return exp(- (delta ** 2) / (2 * (sigma ** 2)))


def theta_for_two_clusters(L2_A, L2_B, sigma=1.0):
    """
    Calcula θ para dos clusters A y B y devuelve un diccionario.

    L2_A: valor L2 del cluster A.
    L2_B: valor L2 del cluster B.
    sigma: mismo parámetro de dispersión usado en compute_theta.

    Retorna:
        {
            "A": θ(L2_A),
            "B": θ(L2_B),
            "mean": promedio de θ(A) y θ(B)
        }
    """
    theta_A = compute_theta(L2_A, sigma=sigma)
    theta_B = compute_theta(L2_B, sigma=sigma)
    mean_theta = (theta_A + theta_B) / 2.0

    return {
        "A": theta_A,
        "B": theta_B,
        "mean": mean_theta,
    }
