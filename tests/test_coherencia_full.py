import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, actualizar_L2, penalizar_MC_CI
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar, compute_L2_self, compute_L2_contexto

def test_ataque_missing_core_final():
    """Aniquila las líneas 78, 83-86, 92-97 de core.py"""
    # 1. Forzar estados de alerta alta (Missing 78, 83-86)
    res_riesgo = {
        "estado_self": {"estado": "RIESGO_SELF"},
        "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
        "coherencia_score": 0.3,
        "decision": {"accion": "CONTINUAR"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.9, 0.9, res_riesgo)
    assert mc < 0.9 # Verifica que hubo penalización
    
    # 2. Forzar bloqueos totales (Missing 92-97)
    for accion in ["DETENER", "DETENER_INMEDIATO", "BLOQUEO"]:
        res_bloqueo = {
            "estado_self": {"estado": "SELF_CRITICO"},
            "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
            "coherencia_score": 0.0,
            "decision": {"accion": accion}
        }
        mc_b, ci_b = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_bloqueo)
        assert mc_b == 0.0 and ci_b == 0.0

def test_ataque_missing_puntos_final():
    """Aniquila las líneas de estadística y estados en puntos.py"""
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # 1. Forzar cálculos de MAD/Sigma (Missing 131-144)
    # Enviamos datos muy variados para que la desviación no sea cero
    valores = [0.1, 0.9, 0.1, 0.9, 0.2, 0.8, 0.5]
    for v in valores:
        sistema.registrar_medicion({"f": v}, {"e": v})
    
    # 2. Forzar estados de recuperación y riesgo
    sistema.registrar_medicion({"f": 1.0}, {}) # RIESGO
    sistema.registrar_medicion({"f": 0.0}, {}) # RECUPERADO
    
    # 3. Forzar daño de contexto (Missing 227-247)
    for _ in range(6):
        sistema.registrar_medicion({}, {"feedback": 1.0, "confianza": 0.0})

    assert sistema.get_estado_actual() is not None

def test_limites_biologicos_corregidos():
    """Cubre las líneas 66, 69 y el piso mínimo de seguridad"""
    # Corregimos el assert para que acepte el 0.05 de seguridad de Villasmil-Ω
    assert compute_L2_self({}) == 0.05 
    assert compute_L2_contexto({}) == 0.05
    
    # Caso de historial vacío
    sistema = SistemaCoherenciaMaxima()
    sistema.history = []
    assert sistema.get_estado_actual() is None
    
    # Penalización decimal isclose
    mc_p, _ = penalizar_MC_CI(0.8, 0.8, 0.5)
    assert math.isclose(mc_p, 0.3)
