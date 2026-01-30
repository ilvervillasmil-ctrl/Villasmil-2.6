# Package init + minimal core implementation for tests
# Coloca este archivo en villasmil_omega/__init__.py

from typing import List, Dict, Tuple

__all__ = [
    "compute_theta",
    "update_L2",
    "apply_penalties",
    "compute_R",
    "ppr_suggest",
]

def compute_theta(premises: List[Dict]) -> float:
    """Si las premisas son idénticas -> 0.0, sino proporción simple de claves en conflicto."""
    if not premises:
        return 0.0
    constraints_list = [p.get("constraints", {}) for p in premises]
    first = constraints_list[0]
    if all(c == first for c in constraints_list):
        return 0.0
    keys = set().union(*constraints_list)
    conflicts = 0
    for k in keys:
        vals = {c.get(k) for c in constraints_list}
        if len(vals - {None}) > 1:
            conflicts += 1
    return conflicts / max(1, len(keys))

def update_L2(L2_current: float) -> float:
    """Aumenta ligeramente L2 para asegurar cambio positivo."""
    return L2_current + max(1e-3, L2_current * 0.05)

def apply_penalties(MC: float, CI: float, L2_current: float) -> Tuple[float, float]:
    """Aplica una penalización simple proporcional a L2 sobre MC y CI."""
    factor = max(0.0, 1.0 - float(L2_current))
    return MC * factor, CI * factor

def compute_R(MC: float, CI: float, phi_C: float, alpha: float, beta: float, gamma: float, n: int) -> float:
    """Cálculo simple de relevancia: producto de calidades menos una penalidad."""
    base = MC * CI
    penalty = phi_C * (alpha + beta + gamma)
    R = base - penalty
    return R if R > 0 else 1e-6

def ppr_suggest(proposal: Dict, context: Dict) -> Dict:
    """Sugiere aceptar o una alternativa basada en L2 y contexto (phi_C)."""
    L2 = float(proposal.get("L2", 1.0))
    phi_C = float(context.get("phi_C", 1.0))
    accepted = (L2 < 0.2) or (phi_C < 0.1)
    alternative = {
        "L2": max(0.05, L2 * 0.9),
        "reason": "lower L2 to improve acceptance"
    }
    return {"accepted": accepted, "alternative": alternative}
