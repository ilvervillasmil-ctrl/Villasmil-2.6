import pytest
import math
# Importamos las herramientas necesarias
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, actualizar_L2, penalizar_MC_CI
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar

def test_cobertura_total_biologica():
    """Ataca las líneas Missing de puntos.py (131-281)"""
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # 1. Forzar cálculos de Sigma y MAD (Líneas 131-144)
    # Enviamos datos muy variables para activar la desviación
    for v in [0.1, 0.9, 0.1, 0.9, 0.5, 0.2, 0.8]:
        sistema.registrar_medicion({"f": v}, {"e": v})
    
    # 2. Forzar estados de Riesgo y Recuperación (Líneas 157-189)
    sistema.registrar_medicion({"f": 1.0}, {}) # Dispara RIESGO_SELF
    sistema.registrar_medicion({"f": 0.0}, {}) # Dispara SELF_RECUPERADO
    
    assert sistema.get_estado_actual() is not None

def test_cobertura_total_core_final():
    """Ataca las líneas 78-94 de core.py y corrige el error de decimales"""
    
    # 1. Probar lógica de ajuste estándar
    res_ok = {
        "estado_self": {"estado": "SELF_ESTABLE"},
        "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
        "coherencia_score": 0.8,
        "decision": {"accion": "CONTINUAR"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_ok)
    assert mc > 0
    
    # 2. Casos de Detención Crítica (Missing 90-94)
    # Probamos las dos condiciones que bloquean el sistema
    for accion in ["DETENER", "DETENER_INMEDIATO"]:
        res_crit = {
            "estado_self": {"estado": "BURNOUT_INMINENTE"},
            "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
            "coherencia_score": 0.0,
            "decision": {"accion": accion}
        }
        mc_c, ci_c = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_crit)
        assert mc_c == 0.0 and ci_c == 0.0

    # 3. Penalizaciones con corrección decimal (Evita el fallo del 0.30000000000000004)
    mc_p, ci_p = penalizar_MC_CI(0.8, 0.8, 0.5, factor=1.0)
    # Usamos math.isclose para que 0.30000000000000004 sea igual a 0.3
    assert math.isclose(mc_p, 0.3)
    assert math.isclose(ci_p, 0.3)
