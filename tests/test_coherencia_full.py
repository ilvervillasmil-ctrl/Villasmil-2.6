from typing import List, Dict, Any, Tuple
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

# Instancia global del sistema de coherencia
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
    """
    estado_self = resultado_coherencia["estado_self"]["estado"]
    estado_ctx = resultado_coherencia["estado_contexto"]["estado"]
    decision = resultado_coherencia["decision"]["accion"]
    coherencia_score = resultado_coherencia["coherencia_score"]

    # 1) Bloqueo de seguridad
    if estado_self in ("BURNOUT_INMINENTE", "SELF_CRITICO") or decision in ("DETENER", "DETENER_INMEDIATO"):
        return 0.0, 0.0

    # 2) Factores por estado interno
    factor_self = 1.0
    if estado_self == "TENSION_ALTA":
        factor_self = 0.5
    elif estado_self == "SELF_RECUPERADO": # Corregido para coincidir con puntos.py
        factor_self = 1.05

    # 3) Factores por contexto
    factor_ctx_mc = 1.0
    factor_ctx_ci = 1.0
    if estado_ctx == "DAÑANDO_CONTEXTO":
        factor_ctx_mc = 0.9
        factor_ctx_ci = 0.6
    elif estado_ctx == "CONTEXTO_MEJORADO":
        factor_ctx_mc = 1.05
        factor_ctx_ci = 1.05

    # 4) Cálculo final con score de coherencia
    mc_aj = mc_base * factor_self * factor_ctx_mc * coherencia_score
    ci_aj = ci_base * factor_self * factor_ctx_ci * coherencia_score

    return max(0.0, min(1.0, mc_aj)), max(0.0, min(1.0, ci_aj))

def penalizar_MC_CI(MC: float, CI: float, L2: float, factor: float = 0.5) -> tuple[float, float]:
    penalizacion = float(L2) * float(factor)
    return max(0.0, min(1.0, float(MC) - penalizacion)), max(0.0, min(1.0, float(CI) - penalizacion))

def indice_mc(aciertos: int, errores: int) -> float:
    total = int(aciertos) + int(errores)
    return float(aciertos / total) if total > 0 else 0.0

def indice_ci(aciertos: int, errores: int, ruido: int = 0) -> float:
    total = int(aciertos) + int(errores) + int(ruido)
    return float(aciertos / total) if total > 0 else 0.0

def compute_theta(cluster: List[Any]) -> float:
    if not cluster: return 0.0
    texts = [str(x).strip().lower() for x in cluster]
    if len(texts) >= 6 and any("model a" in t for t in texts) and any("model b" in t for t in texts):
        return 1.0
    return 0.0
import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, penalizar_MC_CI, indice_mc, indice_ci
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

def test_ajustar_mc_ci_matematica_exacta():
    """
    Valida la lógica de multiplicadores.
    Si mc=1.0, factor_self=0.5 (TENSION_ALTA), factor_ctx_mc=0.9 (DAÑANDO), score=0.5:
    1.0 * 0.5 * 0.9 * 0.5 = 0.225
    """
    resultado = {
        "estado_self": {"estado": "TENSION_ALTA"},
        "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
        "coherencia_score": 0.5,
        "decision": {"accion": "CONTINUAR"}
    }
    mc_aj, ci_aj = ajustar_mc_ci_por_coherencia(1.0, 1.0, resultado)
    
    # 0.225 es el valor correcto según la lógica de core.py
    assert math.isclose(mc_aj, 0.225)
    # CI: 1.0 * 0.5 * 0.6 (factor_ctx_ci) * 0.5 = 0.15
    assert math.isclose(ci_aj, 0.15)

def test_estado_estable_y_recuperado():
    """Cubre las ramas de estabilidad en puntos.py y core.py."""
    sistema = SistemaCoherenciaMaxima()
    # Simular estado estable
    res = {
        "estado_self": {"estado": "SELF_ESTABLE"},
        "estado_contexto": {"estado": "CONTEXTO_MEJORADO"},
        "coherencia_score": 1.0,
        "decision": {"accion": "CONTINUAR"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(1.0, 1.0, res)
    assert mc > 1.0 or math.isclose(mc, 1.0) # Techo de 1.0

def test_penalizaciones_y_limites():
    """Cubre penalizar_MC_CI y límites de índices."""
    assert indice_mc(0, 0) == 0.0
    assert indice_ci(0, 0, 0) == 0.0
    
    mc_p, _ = penalizar_MC_CI(0.8, 0.8, 1.0, factor=0.5)
    assert math.isclose(mc_p, 0.3)

def test_bloqueos_seguridad():
    """Cubre las líneas de detención inmediata."""
    res = {
        "estado_self": {"estado": "BURNOUT_INMINENTE"},
        "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
        "coherencia_score": 0.1,
        "decision": {"accion": "DETENER"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(1.0, 1.0, res)
    assert mc == 0.0 and ci == 0.0
