def ajustar_L2(L2_base, bio_effect):
    """Aplica el efecto biológico y acota al rango absoluto [0, 1]."""
    L2 = float(L2_base + bio_effect)
    # Forzamos evaluación explícita para asegurar cobertura de ramas
    if L2 < 0.0:
        return 0.0
    if L2 > 1.0:
        return 1.0
    return L2

def compute_L2_final(phi_c, theta_c, mc, ci, bio_terms, bio_max, context_mult, min_L2, max_L2):
    # ... lógica previa igual ...
    bio_effect = apply_bio_adjustment(bio_terms, bio_max=bio_max)
    L2_base = compute_L2_base(mc, ci, phi_c=phi_c, theta_c=theta_c, context_mult=context_mult)
    L2 = ajustar_L2(L2_base, bio_effect)

    # Swap de seguridad (Líneas 87-91)
    if min_L2 > max_L2:
        min_L2, max_L2 = max_L2, min_L2

    # Clamp operativo
    if L2 < min_L2:
        L2 = min_L2
    elif L2 > max_L2:
        L2 = max_L2

    # Lógica de saturación final
    if bio_max > 0 and L2 >= bio_max and max_L2 > bio_max:
        L2 = max_L2

    return {"L2": round(L2, 4)}
