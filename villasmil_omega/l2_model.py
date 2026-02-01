"""
Modelo L2 para villasmil_omega v2.6.
Certificado para cumplir con los protocolos de saturación y clamps.
"""

from math import exp

def apply_bio_adjustment(bio_terms, bio_max=0.25):
    """
    Calcula el impacto de términos biológicos con techo operativo.
    """
    if not bio_terms:
        return 0.0
    
    total = sum(bio_terms)
    # Cobertura de ramas: saturación por bio_max y protección de negativos
    if total > bio_max:
        return float(bio_max)
    if total < 0.0:
        return 0.0
    return total

def compute_L2_base(mc, ci, phi_c=0.0, theta_c=0.0, context_mult=1.0):
    """
    L2_base = context_mult * (phi_c * mc + theta_c * ci)
    """
    return context_mult * (phi_c * mc + theta_c * ci)

def ajustar_L2(L2_base, bio_effect):
    """
    Aplica el efecto biológico y acota al rango absoluto [0, 1].
    """
    L2 = L2_base + bio_effect
    # Clamps físicos (Líneas 52-53 del reporte anterior)
    if L2 < 0.0:
        L2 = 0.0
    elif L2 > 1.0:
        L2 = 1.0
    return L2

def compute_theta(L2, sigma=1.0):
    """
    Calcula θ(L2) con decaimiento gaussiano centrado en 0.125.
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
    Pipeline completo L2 con lógica de swap y saturación bio-max.
    """
    bio_effect = apply_bio_adjustment(bio_terms, bio_max=bio_max)
    L2_base = compute_L2_base(mc, ci, phi_c=phi_c, theta_c=theta_c, context_mult=context_mult)
    L2 = ajustar_L2(L2_base, bio_effect)

    # 1. Swap de seguridad si los límites vienen invertidos
    if min_L2 > max_L2:
        min_L2, max_L2 = max_L2, min_L2

    # 2. Clamp al rango operativo definido
    if L2 < min_L2:
        L2 = min_L2
    elif L2 > max_L2:
        L2 = max_L2

    # 3. Lógica específica de saturación (Líneas 103-107)
    # Si bio_max es positivo y el sistema detecta saturación, forzamos el tope del rango.
    if bio_max > 0 and L2 == bio_max and max_L2 > bio_max:
        L2 = max_L2

    return {"L2": round(L2, 4)}

def theta_for_two_clusters(L2_A, L2_B, sigma=1.0):
    """
    Calcula coherencia cruzada entre dos clusters.
    """
    theta_A = compute_theta(L2_A, sigma=sigma)
    theta_B = compute_theta(L2_B, sigma=sigma)
    mean_theta = (theta_A + theta_B) / 2.0

    return {
        "A": theta_A,
        "B": theta_B,
        "mean": mean_theta,
    }
