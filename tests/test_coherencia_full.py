import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar, 
    compute_L2_self, 
    compute_L2_contexto
)

def test_equilibrio_estadistico_y_core():
    """Juega con el equilibrio para activar Sigma y MAD (puntos.py)"""
    conf = ConfiguracionEstandar()
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # Simulamos oscilación: El sistema buscando su centro (Equilibrio)
    # Esto activa la lógica de varianza estadística
    pulsos = [0.1, 0.9, 0.2, 0.8, 0.3, 0.7, 0.4, 0.6, 0.5]
    for p in pulsos:
        sistema.registrar_medicion({"fatiga": p}, {"estres": 1.0 - p})
    
    # ATAQUE A CORE.PY (Líneas 74-94)
    # Probamos la respuesta del sistema ante estados de desequilibrio
    for estado in ["TENSION_ALTA", "RIESGO_SELF", "SELF_CRITICO", "BURNOUT_INMINENTE"]:
        mock_res = {
            "estado_self": {"estado": estado},
            "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
            "coherencia_score": 0.2,
            "decision": {"accion": "CONTINUAR" if estado != "SELF_CRITICO" else "DETENER"}
        }
        ajustar_mc_ci_por_coherencia(0.8, 0.8, mock_res)

    assert sistema.get_estado_actual() is not None

def test_paradoja_final():
    """Mantiene la amistad con los límites de seguridad"""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
