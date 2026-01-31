import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar, 
    compute_L2_self, 
    compute_L2_contexto
)

def test_ataque_quirurgico_l2():
    """Ataca específicamente las líneas 131-281 de puntos.py y 77-107 de core.py"""
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # 1. FORZAR ESTADÍSTICAS (Líneas 131-144)
    # Necesitamos mucha variabilidad para que Sigma y MAD se calculen
    for v in [0.1, 0.9, 0.1, 0.9, 0.2, 0.8, 0.5, 0.4, 0.6]:
        sistema.registrar_medicion({"f": v}, {"e": v})
    
    # 2. FORZAR ESTADOS CRÍTICOS (Líneas 157-189)
    sistema.registrar_medicion({"f": 1.0}, {"e": 1.0}) # DISPARA RIESGO
    sistema.registrar_medicion({"f": 0.05}, {"e": 0.05}) # DISPARA RECUPERACIÓN
    
    # 3. FORZAR DAÑO DE CONTEXTO (Líneas 227-253)
    for _ in range(10):
        sistema.registrar_medicion({}, {"feedback_negativo": 1.0, "caos": 1.0})

    # 4. ILUMINAR CORE.PY (Líneas 77-107)
    # Creamos un resultado que obligue a core a usar la lógica de coherencia
    res_mock = sistema.get_estado_actual()
    # Aseguramos que la decisión no sea DETENER para entrar en los ajustes
    res_mock["decision"]["accion"] = "CONTINUAR" 
    mc, ci = ajustar_mc_ci_por_coherencia(0.8, 0.8, res_mock)
    
    assert mc != 0.8 # Si es diferente, es que core.py trabajó.

def test_puntos_extra_edges():
    """Cubre las líneas sueltas 66, 69 y 281"""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
    sistema = SistemaCoherenciaMaxima()
    sistema.history = []
    assert sistema.get_estado_actual() is None
