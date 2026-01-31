"""
Villasmil-Ω — core coherence utilities
"""

from typing import List, Dict, Any


def suma_omega(a: float, b: float) -> float:
    """
    Suma simple usada en tests básicos.
    """
    return float(a) + float(b)


def indice_mc(mc_values: List[float]) -> float:
    """
    Índice simple de MC:
    - Recibe una lista de valores MC en [0,1].
    - Devuelve el promedio (también en [0,1]).
    """
    if not mc_values:
        return 0.0
    s = sum(float(x) for x in mc_values)
    return float(s / len(mc_values))


def indice_ci(ci_values: List[float]) -> float:
    """
    Índice simple de CI:
    - Misma idea que indice_mc, pero para CI.
    """
    if not ci_values:
        return 0.0
    s = sum(float(x) for x in ci_values)
    return float(s / len(ci_values))


def compute_theta(cluster: List[Dict[str, Any]]) -> float:
    """
    Compute Θ(C) for a cluster of premises.
    """
    if not cluster:
        return 0.0

    bool_values: List[bool] = []
    for item in cluster:
        v = item.get("value", True)
        if isinstance(v, (int, float)):
            bool_values.append(bool(v))
        else:
            bool_values.append(bool(v))

    total = len(bool_values)
    trues = sum(1 for v in bool_values if v)
    falses = total - trues

    p_true = trues / total
    p_false = falses / total

    theta = min(p_true, p_false)
    return float(theta)


def theta_for_two_clusters(c1: List[Dict[str, Any]], c2: List[Dict[str, Any]]) -> Dict[str, float]:
    """
    Helper opcional: devuelve Θ(C1), Θ(C2) y Θ(C1 ∪ C2).
    """
    combined = c1 + c2
    theta_c1 = compute_theta(c1)
    theta_c2 = compute_theta(c2)
    theta_combined = compute_theta(combined)
    return {
        "theta_c1": theta_c1,
        "theta_c2": theta_c2,
        "theta_combined": theta_combined,
    }
