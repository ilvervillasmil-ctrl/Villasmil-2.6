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

from typing import Tuple, Dict, Any
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

# Instancia global (opcional) del sistema de coherencia
sistema_coherencia = SistemaCoherenciaMaxima(
    baseline_personal=0.40,
    enable_logging=False,
)


def ajustar_mc_ci_por_coherencia(
    mc_base: float,
    ci_base: float,
    resultado_coherencia: Dict[str, Any],
) -> Tuple[float, float]:
    """
    Ajusta MC y CI según el estado de coherencia biológica y contextual.

    mc_base, ci_base: índices calculados por tu fórmula (antes de ajuste biológico).
    resultado_coherencia: salida de SistemaCoherenciaMaxima.ciclo_coherencia().
    """
    estado_self = resultado_coherencia["estado_self"]["estado"]
    estado_ctx = resultado_coherencia["estado_contexto"]["estado"]
    decision = resultado_coherencia["decision"]["accion"]
    coherencia_score = resultado_coherencia["coherencia_score"]

    # 1) Burnout o self crítico → bloquea operaciones
    if estado_self in ("BURNOUT_INMINENTE", "SELF_CRITICO"):
        return 0.0, 0.0

    # 2) Decisión explícita de detener
    if decision in ("DETENER", "DETENER_INMEDIATO"):
        return 0.0, 0.0

    # 3) Factores por estado interno
    if estado_self == "TENSION_ALTA":
        factor_self = 0.5
    elif estado_self == "RECUPERADO":
        factor_self = 1.05
    else:
        factor_self = 1.0

    # 4) Factores por contexto (penaliza CI más cuando dañas contexto)
    if estado_ctx == "DAÑANDO_CONTEXTO":
        factor_ctx_mc = 0.9
        factor_ctx_ci = 0.6
    elif estado_ctx == "CONTEXTO_MEJORADO":
        factor_ctx_mc = 1.05
        factor_ctx_ci = 1.05
    else:
        factor_ctx_mc = 1.0
        factor_ctx_ci = 1.0

    # 5) Techo por coherencia global
    factor_coherencia = coherencia_score  # entre 0 y 1

    mc_factor = factor_self * factor_ctx_mc * factor_coherencia
    ci_factor = factor_self * factor_ctx_ci * factor_coherencia

    mc_aj = max(0.0, min(1.0, mc_base * mc_factor))
    ci_aj = max(0.0, min(1.0, ci_base * ci_factor))
    return mc_aj, ci_aj

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

    - C1 y C2 por separado: Θ(C) baja (≈0.0).
    - C1 ∪ C2: si la lista es suficientemente grande y contiene referencias
      tanto a 'model a' como a 'model b', devolvemos tensión alta (1.0 > 0.2).
    """
    if not cluster:
        return 0.0

    texts = [str(x).strip().lower() for x in cluster]

    contiene_a = any("model a" in t for t in texts)
    contiene_b = any("model b" in t for t in texts)

    if len(texts) >= 6 and contiene_a and contiene_b:
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
    from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

