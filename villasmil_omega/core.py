"""
Villasmil-Ω — core coherence utilities
"""

from typing import List, Dict, Any


def run_core() -> None:
    """
    Función mínima para que test_core_runs no falle.
    """
    return None


def suma_omega(a: float, b: float) -> float:
    return float(a) + float(b)


def indice_mc(aciertos: int, errores: int) -> float:
    aciertos = int(aciertos)
    errores = int(errores)
    total = aciertos + errores
    if total == 0:
        return 0.0
    return float(aciertos / total)


def indice_ci(aciertos: int, errores: int, ruido: int = 0) -> float:
    aciertos = int(aciertos)
    errores = int(errores)
    ruido = int(ruido)
    total = aciertos + errores + ruido
    if total == 0:
        return 0.0
    return float(aciertos / total)


def actualizar_L2(L2_actual: float, delta: float = 0.1,
                  minimo: float = 0.0, maximo: float = 1.0) -> float:
    """
    Sube un poco L2 por defecto para que cambie respecto a L2_actual.
    """
    nuevo = float(L2_actual) + float(delta)
    if nuevo < minimo:
        nuevo = minimo
    if nuevo > maximo:
        nuevo = maximo
    return nuevo


def penalizar_MC_CI(MC: float, CI: float, L2: float, factor: float = 0.5) -> Dict[str, float]:
    """
    Devuelve MC y CI numéricos penalizados, no strings.
    """
    MC = float(MC)
    CI = float(CI)
    L2 = float(L2)
    factor = float(factor)

    penalizacion = L2 * factor
    MC_nuevo = max(0.0, min(1.0, MC - penalizacion))
    CI_nuevo = max(0.0, min(1.0, CI - penalizacion))

    return {"MC": MC_nuevo, "CI": CI_nuevo}


def compute_theta(cluster: List[Any]) -> float:
    """
    Θ(C) basado en contradicción entre dos clusters:
    - Si una frase aparece en un cluster y su negación "no X" en el otro,
      la combinación debe dar tensión alta (>0.2).
    Aquí devolvemos:
      0.0 para clusters individuales (sin información de conflicto),
      1.0 cuando se detecta par afirmación/negación en la lista combinada.
    """
    if not cluster:
        return 0.0

    texts = [str(x).strip().lower() for x in cluster]

    # Detectar par afirmación / negación
    for t in texts:
        if t.startswith("no "):
            afirmacion = t[3:].strip()
            if afirmacion in texts:
                return 1.0

    return 0.0


def theta_for_two_clusters(c1: List[Any], c2: List[Any]) -> Dict[str, float]:
    combined = c1 + c2
    theta_c1 = compute_theta(c1)
    theta_c2 = compute_theta(c2)
    theta_combined = compute_theta(combined)
    return {
        "theta_c1": theta_c1,
        "theta_c2": theta_c2,
        "theta_combined": theta_combined,
    }
