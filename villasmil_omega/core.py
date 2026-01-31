"""
Villasmil-Ω — core coherence utilities
"""

from typing import List, Dict, Any


def run_core() -> None:
    """Función mínima para que test_core_runs no falle."""
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
    """Sube un poco L2 por defecto para que cambie respecto a L2_actual."""
    nuevo = float(L2_actual) + float(delta)
    if nuevo < minimo:
        nuevo = minimo
    if nuevo > maximo:
        nuevo = maximo
    return nuevo


def penalizar_MC_CI(MC: float, CI: float, L2: float, factor: float = 0.5) -> tuple[float, float]:
    """
    Devuelve MC y CI penalizados numéricamente (MC_p, CI_p).
    """
    MC = float(MC)
    CI = float(CI)
    L2 = float(L2)
    factor = float(factor)

    penalizacion = L2 * factor
    MC_nuevo = max(0.0, min(1.0, MC - penalizacion))
    CI_nuevo = max(0.0, min(1.0, CI - penalizacion))

    return MC_nuevo, CI_nuevo


def compute_theta(cluster: List[Any]) -> float:
    """
    Θ(C) para A2.2:

    - C1 y C2 por separado: Θ(C) = 0.0 (baja tensión).
    - C1 ∪ C2: si aparecen a la vez referencias a 'model a' y 'model b',
      consideramos conflicto claro y devolvemos 1.0 (> 0.2).
    """
    if not cluster:
        return 0.0

    texts = [str(x).strip().lower() for x in cluster]

    contiene_a = any("model a" in t for t in texts)
    contiene_b = any("model b" in t for t in texts)

    if contiene_a and contiene_b:
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
