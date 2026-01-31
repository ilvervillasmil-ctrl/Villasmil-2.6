import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, penalizar_MC_CI, indice_mc, indice_ci
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

# ============================================================
# ATAQUE A CORE.PY (Líneas 67-107: Casos Borde y Penalizaciones)
# ============================================================

def test_core_indices_extremos():
    """Cubre las ramas de división por cero y valores atípicos en core."""
    assert indice_mc(0, 0) == 0.0
    assert indice_ci(0, 0, 0) == 0.0
    assert indice_mc(10, 0) == 1.0
    assert indice_ci(10, 0, 5) == 10/15

def test_penalizar_mc_ci_variaciones():
    """Cubre la lógica de penalización con diferentes factores L2."""
    # Caso L2 alto (penalización máxima)
    mc_p, ci_p = penalizar_MC_CI(0.8, 0.8, 1.0, factor=0.5)
    assert mc_p == 0.3 # 0.8 - (1.0 * 0.5)
    
    # Caso L2 que lleva a cero
    mc_p, ci_p = penalizar_MC_CI(0.2, 0.2, 1.0, factor=0.9)
    assert mc_p == 0.0

def test_ajustar_mc_ci_estados_criticos():
    """Fuerza las ramas lógicas de TENSION_ALTA y DAÑANDO_CONTEXTO en core."""
    resultado = {
        "estado_self": {"estado": "TENSION_ALTA"},
        "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
        "coherencia_score": 0.5,
        "decision": {"accion": "DETENER"} # Aunque diga detener, probamos multiplicadores
    }
    # En TENSION_ALTA f_self = 0.5. En DAÑANDO_CONTEXTO f_ctx_ci = 0.6. Score = 0.5.
    mc_aj, ci_aj = ajustar_mc_ci_por_coherencia(1.0, 1.0, resultado)
    
    # MC_aj = 1.0 * 0.5 (self) * 0.5 (score) = 0.25
    # CI_aj = 1.0 * 0.5 (self) * 0.6 (ctx) * 0.5 (score) = 0.15
    assert math.isclose(mc_aj, 0.25)
    assert math.isclose(ci_aj, 0.15)

# ============================================================
# ATAQUE A PUNTOS.PY (Líneas 127-177: MAD, Sigma y EWMA)
# ============================================================

def test_estres_estadistico_l2():
    """Fuerza la actualización de la MAD y el cálculo de Sigmas en puntos.py."""
    conf = ConfiguracionEstandar(ALPHA_SELF=0.8, K_SELF=2.0)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # 1. Creamos una montaña rusa de datos para disparar la desviación (MAD)
    valores = [0.1, 0.9, 0.1, 0.9, 0.2, 0.8]
    for v in valores:
        res = sistema.registrar_medicion({"fatiga_fisica": v}, {})
        
    # Verificamos que la MAD y Sigma ya no son cero
    assert res["sigma_self"] > 0
    assert res["deadband_self"] >= conf.DELTA_ABS_SELF

def test_l2_compute_con_señales_incompletas():
    """Cubre las ramas de diccionarios vacíos y valores por defecto."""
    # Diccionario vacío debe devolver un valor basado en la inversión de 0.5 (por defecto)
    l2_s = compute_L2_self({})
    l2_c = compute_L2_contexto({})
    assert 0.0 <= l2_s <= 1.0
    assert 0.0 <= l2_c <= 1.0
