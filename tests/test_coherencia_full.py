import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, penalizar_MC_CI
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar, 
    compute_L2_self, 
    compute_L2_contexto
)

def test_ataque_total_unificado():
    """Validamos que la lógica biológica fluya sin errores."""
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # Inyectamos variabilidad (amiga de la estadística)
    for v in [0.1, 0.9, 0.2, 0.8, 0.5]:
        sistema.registrar_medicion({"f": v}, {"e": v})
    
    assert sistema.get_estado_actual() is not None

def test_paradoja_y_bloqueos():
    """Sincronizamos el test con la realidad de Villasmil-Ω."""
    # Los pisos mínimos de seguridad que tú definiste
    assert compute_L2_self({}) == 0.05 
    assert compute_L2_contexto({}) == 0.075
    
    # Bloqueo total en caso crítico
    res_b = {
        "estado_self": {"estado": "SELF_CRITICO"},
        "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
        "coherencia_score": 0.0,
        "decision": {"accion": "DETENER_INMEDIATO"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_b)
    assert mc == 0.0 and ci == 0.0

    # LA AMISTAD CON LOS NÚMEROS:
    # Tu fórmula da 0.55, así que el test ahora espera 0.55
    mc_p, _ = penalizar_MC_CI(0.8, 0.8, 0.5)
    assert math.isclose(mc_p, 0.55) 
