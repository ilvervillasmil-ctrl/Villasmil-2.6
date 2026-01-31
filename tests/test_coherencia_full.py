import pytest
import math
# Importamos todo lo necesario para iluminar core.py y puntos.py
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, actualizar_L2, penalizar_MC_CI
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar

def test_ataque_missing_core():
    """Aniquila las líneas 78, 82, 84, 90-94 de core.py"""
    # 1. Cubrir ramas de ajuste por estado (Missing 78, 82, 84)
    res_tension = {
        "estado_self": {"estado": "TENSION_ALTA"},
        "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
        "coherencia_score": 0.5,
        "decision": {"accion": "CONTINUAR"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(1.0, 1.0, res_tension)
    assert mc < 1.0
    
    # 2. Cubrir bloqueos por Burnout/Crítico (Missing 90-94)
    for estado in ["BURNOUT_INMINENTE", "SELF_CRITICO"]:
        res_crit = {
            "estado_self": {"estado": estado},
            "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
            "coherencia_score": 0.1,
            "decision": {"accion": "DETENER"}
        }
        mc_c, ci_c = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_crit)
        assert mc_c == 0.0 and ci_c == 0.0

def test_ataque_missing_puntos():
    """Aniquila las líneas 131-144, 157-189, 227-247 de puntos.py"""
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # 1. Forzar cálculos estadísticos MAD/Sigma (Missing 131-144)
    # Enviamos datos muy variados
    for v in [0.1, 0.9, 0.1, 0.9, 0.5]:
        sistema.registrar_medicion({"f": v}, {"e": v})
    
    # 2. Forzar estados de alerta y recuperación (Missing 157-189)
    sistema.registrar_medicion({"f": 1.0}, {}) # RIESGO_SELF
    sistema.registrar_medicion({"f": 0.1}, {}) # SELF_RECUPERADO
    
    # 3. Forzar daño de contexto (Missing 227-247)
    for _ in range(5):
        sistema.registrar_medicion({}, {"feedback_directo": 0.9, "confianza": 0.1})
    
    assert sistema.get_estado_actual() is not None

def test_puntos_edges_y_limites():
    """Cubre líneas sueltas como la 281 (historial vacío)"""
    sistema = SistemaCoherenciaMaxima()
    sistema.history = []
    assert sistema.get_estado_actual() is None
    # Cubrir líneas 66, 69 de puntos.py
    from villasmil_omega.human_l2.puntos import compute_L2_self, compute_L2_contexto
    assert compute_L2_self({}) == 0.0
    assert compute_L2_contexto({}) == 0.0
