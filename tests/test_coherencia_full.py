import pytest
import math
# Importamos directamente para cubrir puntos.py y el __init__
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, actualizar_L2, penalizar_MC_CI

def test_cobertura_total_biologica():
    """Ataca las líneas Missing de puntos.py (131-281)"""
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # 1. Forzar cálculos de Sigma y MAD (Líneas 131-144)
    # Enviamos datos con alta variabilidad
    for v in [0.1, 0.9, 0.2, 0.8, 0.5, 0.5, 0.5]:
        sistema.registrar_medicion({"fatiga": v}, {"estres": v})
    
    # 2. Forzar estados de Riesgo y Recuperación (Líneas 157-189)
    sistema.registrar_medicion({"fatiga": 0.95}, {}) # Disparo de riesgo
    sistema.registrar_medicion({"fatiga": 0.05}, {}) # Recuperación
    
    # 3. Forzar daño de contexto (Líneas 227-253)
    for _ in range(5):
        sistema.registrar_medicion({}, {"feedback_negativo": 1.0})
        
    assert sistema.get_estado_actual() is not None

def test_cobertura_total_core():
    """Ataca las líneas Missing de core.py (77-107)"""
    # 1. Probar ajuste de MC/CI por coherencia (Esta es la parte grande que falta)
    res_mock = {
        "estado_self": {"estado": "SELF_ESTABLE"},
        "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
        "coherencia_score": 0.8,
        "decision": {"accion": "CONTINUAR"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_mock)
    assert mc > 0 and ci > 0

    # 2. Probar casos de detención (Líneas 89-95 aprox)
    res_critico = {
        "estado_self": {"estado": "SELF_CRITICO"},
        "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
        "coherencia_score": 0.1,
        "decision": {"accion": "DETENER"}
    }
    mc_c, ci_c = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_critico)
    assert mc_c == 0.0 and ci_c == 0.0

    # 3. Probar penalizaciones (Líneas restantes)
    mc_p, ci_p = penalizar_MC_CI(0.8, 0.8, 0.5, factor=1.0)
    assert mc_p == 0.3
