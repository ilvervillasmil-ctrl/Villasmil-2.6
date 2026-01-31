import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

def test_camino_al_cien():
    """Límite físico, mente relajada, propósito claro."""
    sistema = SistemaCoherenciaMaxima()
    
    # 1. PROPÓSITO: Romper la inercia estadística (Puntos 131-144)
    # Una ráfaga de datos asimétricos para forzar el cálculo de Sigma
    for i in range(20):
        v = 0.99 if i % 3 == 0 else 0.01
        sistema.registrar_medicion({"f": v}, {"e": 1.0 - v})

    # 2. LÍMITE FÍSICO: Forzar los estados de Bloqueo (Core 92-97)
    for accion in ["DETENER", "DETENER_INMEDIATO", "BLOQUEO"]:
        res_limite = {
            "estado_self": {"estado": "BURNOUT_INMINENTE"},
            "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
            "coherencia_score": 0.0,
            "decision": {"accion": accion}
        }
        mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_limite)
        assert mc == 0.0 and ci == 0.0 # Apagado total en el límite

    # 3. MENTE RELAJADA: Cubrir ramas de riesgo (Core 78, 84)
    for est in ["RIESGO_SELF", "SELF_CRITICO"]:
        res_riesgo = {
            "estado_self": {"estado": est},
            "estado_contexto": {"estado": "ESTABLE"},
            "coherencia_score": 0.4,
            "decision": {"accion": "CONTINUAR"}
        }
        ajustar_mc_ci_por_coherencia(0.8, 0.8, res_riesgo)

def test_bordes_finales():
    """Limpia las últimas líneas de puntos.py (66, 69, 157, 282)."""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
    
    # Forzar el None en historial vacío (Línea 282)
    s = SistemaCoherenciaMaxima()
    s.history = []
    assert s.get_estado_actual() is None
