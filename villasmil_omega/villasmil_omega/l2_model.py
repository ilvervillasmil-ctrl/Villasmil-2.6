"""
Modelo L2 mejorado: base, ajustes biométricos y clamp final.

L2_base = 0.40·φ_C + 0.30·θ_C + 0.15·(1 − MC) + 0.15·(1 − CI)
L2_raw  = (L2_base + bio_adjustment) * context_mult
L2_final = clamp(L2_raw, min_L2, max_L2)
"""


from typing import Dict, Sequence


def compute_L2_base(
    phi_c: float,
    theta_c: float,
    mc: float,
    ci: float,
) -> float:
    """
    Calcula L2_base a partir de φ_C, θ_C, MC y CI.
    Todos los valores se esperan en [0, 1].
    """
    phi_c = float(phi_c)
    theta_c = float(theta_c)
    mc = float(mc)
    ci = float(ci)

    return (
        0.40 * phi_c
        + 0.30 * theta_c
        + 0.15 * (1.0 - mc)
        + 0.15 * (1.0 - ci)
    )


def apply_bio_adjustment(
    bio_terms: Sequence[float],
    bio_max: float = 0.2,
) -> float:
    """
    Suma los aportes biométricos y los limita por bio_max para evitar 'bloat'.
    """
    total = float(sum(float(x) for x in bio_terms)) if bio_terms else 0.0
    bio_max = float(bio_max)
    if bio_max < 0.0:
        bio_max = 0.0
    return min(total, bio_max)


def compute_L2_final(
    phi_c: float,
    theta_c: float,
    mc: float,
    ci: float,
    bio_terms: Sequence[float] | None = None,
    bio_max: float = 0.2,
    context_mult: float = 1.0,
    min_L2: float = 0.10,
    max_L2: float = 0.95,
) -> Dict[str, float]:
    """
    Calcula L2_final con clamp entre min_L2 y max_L2.

    Devuelve un dict con:
      - L2_base
      - bio_adjustment
      - L2_raw
      - L2
    """
    if bio_terms is None:
        bio_terms = []

    L2_base = compute_L2_base(phi_c, theta_c, mc, ci)
    bio_adj = apply_bio_adjustment(bio_terms, bio_max=bio_max)

    context_mult = float(context_mult)
    L2_raw = (L2_base + bio_adj) * context_mult

    # Normalizar min/max por seguridad
    min_L2 = float(min_L2)
    max_L2 = float(max_L2)
    if max_L2 < min_L2:
        max_L2, min_L2 = min_L2, max_L2  # swap si vienen mal

    # Clamp final
    L2_final = max(min_L2, min(max_L2, float(L2_raw)))

    return {
        "L2_base": float(L2_base),
        "bio_adjustment": float(bio_adj),
        "L2_raw": float(L2_raw),
        "L2": float(L2_final),
    }
