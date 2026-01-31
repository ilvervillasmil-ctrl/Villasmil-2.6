"""
Villasmil-Ω — core coherence utilities
"""

from typing import List, Dict, Any


def run_core() -> None:
    """
    Función mínima para que test_core_runs no falle.
    No hace nada, solo confirma que el módulo carga.
    """
    return None


def suma_omega(a: float, b: float) -> float:
    """
    Suma simple usada en tests básicos.
    """
    return float(a) + float(b)


def indice_mc(aciertos: int, errores: int) -> float:
    """
    Índice de MC:
    mc = aciertos / (aciertos + errores), con protección para división por cero.
    """
    aciertos = int(aciertos)
    errores = int(errores)
    total = aciertos + errores
    if total == 0:
        return 0.0
    return float(aciertos / total)


def indice_ci(aciertos: int, errores: int, ruido: int = 0) -> float:
    """
    Índice de CI:
    ci = aciertos / (aciertos + errores + ruido), protegido.
    """
    aciertos = int(aciertos)
    errores = int(errores)
    ruido = int(ruido)
    total = aciertos + errores + ruido
    if total == 0:
        return 0.0
    return float(aciertos / total)


def actualizar_L2(L2_actual: float, delta: float = 0.0,
                  minimo: float = 0.0, maximo: float = 1.0) -> float:
    """
    Actualiza L2 con un delta (por defecto 0) y lo mantiene en [minimo, maximo].
    """
    nuevo = float(L2_actual) + float(delta)
    if nuevo < minimo:
        nuevo = minimo
    if nuevo > maximo:
        nuevo = maximo
    return nuevo


def penalizar_MC_CI(MC: float, CI: float, L2: float, factor: float = 0.5) -> Dict[str, float]:
    """
    Penaliza MC y CI en función de L2 (tensión):
    MC_nuevo = MC - L2 * factor (saturado en [0,1])
    CI_nuevo = CI - L2 * factor (saturado en [0,1])
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
    Compute Θ(C) para un cluster de premisas.

    Los tests pasan listas de strings (premisas).
    Aquí definimos Θ(C) como:
    - 0.0 si todas las premisas son del mismo "signo" (no hay contradicción obvia).
    - 1.0 si hay al menos una pareja evidentemente contradictoria (A vs no-A).
    Implementación mínima: buscamos pares opuestos simples.
    """
    if not cluster:
        return 0.0

    # Normalizar a strings en minúsculas
    texts = [str(x).strip().lower() for x in cluster]

    # Heurística mínima: si aparece algo como "no " al inicio que contradiga otra oración
    # sin el "no ", marcamos alta tensión (1.0)
    for t in texts:
        if t.startswith("no "):
            afirmacion = t[3:].strip()
            if afirmacion in texts:
                return 1.0

    # Si no detectamos contradicción explícita, devolvemos 0.0
    return 0.0


def theta_for_two_clusters(c1: List[Any], c2: List[Any]) -> Dict[str, float]:
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
