"""
Modelo L2 para villasmil_omega.
"""

from math import exp


def compute_L2_base(MC, CI, w_mc=0.5, w_ci=0.5):
    """
    L2_base = w_mc * MC + w_ci * CI.

    MC: Meta-Consciencia en [0, 1].
    CI: Coherencia Informacional en [0, 1].
    w_mc, w_ci: pesos (por defecto 0.5 y 0.5).
    """
    return w_mc * MC + w_ci * CI


def ajustar_L2(L2_base, ruido=0.0):
    """
    Ajusta L2 con un pequeño término de ruido aditivo y lo acota a [0, 1].
    """
    L2 = L2_base + ruido
    if L2 < 0.0:
        L2 = 0.0
    if L2 > 1.0:
        L2 = 1.0
    return L2


def apply_bio_adjustment(L2, bio_factor=1.0):
    """
    Ajusta L2 por un factor biológico simple:

        L2_bio = L2 * bio_factor

    y lo acota a [0, 1].
    """
    L2_bio = L2 * bio_factor
    if L2_bio < 0.0:
        L2_bio = 0.0
    if L2_bio > 1.0:
        L2_bio = 1.0
    return L2_bio


def compute_theta(L2, sigma=1.0):
    """
    Calcula θ(L2) = exp(−(L2 − 0.125)^2 / (2 * sigma^2)).
    """
    delta = L2 - 0.125
    return exp(- (delta ** 2) / (2 * (sigma ** 2)))


def theta_for_two_clusters(L2_A, L2_B, sigma=1.0):
    """
    Calcula θ para dos clusters A y B y devuelve un diccionario.
    """
    theta_A = compute_theta(L2_A, sigma=sigma)
    theta_B = compute_theta(L2_B, sigma=sigma)
    mean_theta = (theta_A + theta_B) / 2.0

    return {
        "A": theta_A,
        "B": theta_B,
        "mean": mean_theta,
    }
