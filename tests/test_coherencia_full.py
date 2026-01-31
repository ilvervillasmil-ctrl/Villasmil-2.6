import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, penalizar_MC_CI, indice_mc, indice_ci
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

def test_core_indices_extremos():
    assert indice_mc(0, 0) == 0.0
    assert indice_ci(0, 0, 0) == 0.0
    assert indice_mc(10, 0) == 1.0

def test_penalizar_mc_ci_variaciones():
    """Usa isclose para evitar errores de precisión decimal."""
    mc_p, ci_p = penalizar_MC_CI(0.8, 0.8, 1.0, factor=0.5)
    # 0.8 - 0.5 = 0.3. Usamos isclose para el 0.30000000000000004
    assert math.isclose(mc_p, 0.3)
    
    mc_p, ci_p = penalizar_MC_CI(0.2, 0.2, 1.0, factor=0.9)
    assert mc_p == 0.0

def test_ajustar_mc_ci_estados_criticos():
    """Probamos multiplicadores cambiando la acción a 'CONTINUAR'."""
    resultado = {
        "estado_self": {"estado": "TENSION_ALTA"},
        "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
        "coherencia_score": 0.5,
        "decision": {"accion": "CONTINUAR"} # CAMBIADO de DETENER a CONTINUAR
    }
    mc_aj, ci_aj = ajustar_mc_ci_por_coherencia(1.0, 1.0, resultado)
    
    # Cálculos:
    # mc = 1.0 * 0.5 (TENSION_ALTA) * 0.5 (score) = 0.25
    # ci = 1.0 * 0.5 (self) * 0.6 (DAÑANDO_CTX) * 0.5 (score) = 0.15
    assert math.isclose(mc_aj, 0.25)
    assert math.isclose(ci_aj, 0.15)

def test_estres_estadistico_l2():
    conf = ConfiguracionEstandar(ALPHA_SELF=0.8, K_SELF=2.0)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # Oscilación para forzar MAD y Sigma
    for v in [0.1, 0.9, 0.1, 0.9]:
        res = sistema.registrar_medicion({"fatiga_fisica": v}, {})
        
    assert res["sigma_self"] >= 0
    assert "deadband_self" in res

def test_l2_compute_con_señales_incompletas():
    # Cobertura de diccionarios vacíos
    assert 0.0 <= compute_L2_self({}) <= 1.0
    assert 0.0 <= compute_L2_contexto({}) <= 1.0
