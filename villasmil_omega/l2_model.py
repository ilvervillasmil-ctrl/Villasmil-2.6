"""
Modelo L2 para villasmil_omega.
"""

from math import exp


def apply_bio_adjustment(bio_terms, bio_max=0.25):
    """
    Aplica un límite superior a los términos biológicos y devuelve la suma acotada:

        bio_clamped_i = min(term, bio_max)
        return sum(bio_clamped_i)

    Si la lista está vacía, retorna 0.0.
    """
    if not bio_terms:
        return 0.0
    total = 0.0
    for term in bio_terms:
        if term > bio_max:
            term = bio_max
        total += term
    return total


def compute_L2_base(mc, ci, phi_c=0.0, theta_c=0.0, context_mult=1.0):
    """
    Cálculo base de L2 combinando contexto y métricas internas.

        L2_base = context_mult * (phi_c * mc + theta_c * ci)
    """
    return context_mult * (phi_c * mc + theta_c * ci)


def ajustar_L2(L2_base, bio_effect):
    """
    Ajusta L2 sumando el efecto biológico y lo acota a [0, 1].
    """
    L2 = L2_base + bio_effect
    if L2 < 0.0:
        L2 = 0.0
    if L2 > 1.0:
        L2 = 1.0
    return L2


def compute_theta(L2, sigma=1.0):
    """
    Calcula θ(L2) = exp(−(L2 − 0.125)^2 / (2 * sigma^2)).
    """
    delta = L2 - 0.125
    return exp(- (delta ** 2) / (2 * (sigma ** 2)))


def compute_L2_final(
    phi_c,
    theta_c,
    mc,
    ci,
    bio_terms,
    bio_max,
    context_mult,
    min_L2,
    max_L2,
):
    """
    Pipeline completo para L2 con clamps y corrección de límites.

    1) bio_effect = apply_bio_adjustment(bio_terms, bio_max)
    2) L2_base   = compute_L2_base(mc, ci, phi_c, theta_c, context_mult)
    3) L2        = ajustar_L2(L2_base, bio_effect)
    4) Corrige min_L2 y max_L2 si vienen invertidos.
    5) Aplica clamp final a [min_L2, max_L2].
    """
    bio_effect = apply_bio_adjustment(bio_terms, bio_max=bio_max)
    L2_base = compute_L2_base(mc, ci, phi_c=phi_c, theta_c=theta_c, context_mult=context_mult)
    L2 = ajustar_L2(L2_base, bio_effect)

    # Swap si min_L2 > max_L2
    if min_L2 > max_L2:
        min_L2, max_L2 = max_L2, min_L2

    if L2 < min_L2:
        L2 = min_L2
    if L2 > max_L2:
        L2 = max_L2

    return L2


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
