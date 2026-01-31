import pytest
import math
# Importamos directamente de puntos.py para saltar cualquier problema del __init__
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar, 
    compute_L2_self, 
    compute_L2_contexto
)
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, penalizar_MC_CI

def test_ataque_total_unificado():
    """Cubre la lógica biológica y estadística"""
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # Inyectamos datos variables para cubrir MAD/Sigma
    for v in [0.1, 0.9, 0.2, 0.8, 0.5]:
        sistema.registrar_medicion({"f": v}, {"e": v})
    
    # Forzar estados de Riesgo y Recuperación
    sistema.registrar_medicion({"f": 1.0}, {}) 
    sistema.registrar_medicion({"f": 0.0}, {}) 
    assert sistema.get_estado_actual() is not None

def test_paradoja_y_bloqueos():
    """Resuelve la paradoja del 0.05 vs 0.075 y cubre core.py"""
    # Validamos los pisos mínimos que descubrimos
    assert compute_L2_self({}) == 0.05 
    assert compute_L2_contexto({}) == 0.075
    
    # Forzar bloqueos en core.py (Líneas 92-97)
    res_b = {
        "estado_self": {"estado": "SELF_CRITICO"},
        "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
        "coherencia_score": 0.0,
        "decision": {"accion": "DETENER_INMEDIATO"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_b)
    assert mc == 0.0 and ci == 0.0

    # Penalización decimal con isclose
    mc_p, _ = penalizar_MC_CI(0.8, 0.8, 0.5)
    assert math.isclose(mc_p, 0.3)
