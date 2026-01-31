import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar, 
    compute_L2_self, 
    compute_L2_contexto
)

def test_respiracion_biologica_y_equilibrio():
    """Permite que el sistema respire para activar Sigma y MAD."""
    conf = ConfiguracionEstandar()
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # Simulación de inhalación y exhalación (15 ciclos)
    # Esto genera la varianza necesaria para las líneas 131-144 de puntos.py
    for t in range(15):
        # Onda senoidal: la forma más pura de equilibrio en movimiento
        respiracion = 0.5 + 0.4 * math.sin(t * 0.5) 
        sistema.registrar_medicion(
            {"pulso_biologico": respiracion}, 
            {"ritmo_contexto": 1.0 - respiracion}
        )
    
    # Verificamos que tras respirar, el sistema tiene un estado coherente
    estado = sistema.get_estado_actual()
    assert estado is not None
    assert "coherencia_score" in estado

def test_proteccion_en_caos():
    """Verifica que el sistema sabe apagarse si la respiración se corta (Core)."""
    # Forzamos los estados de detención total (Líneas 90-94 de core.py)
    for accion in ["DETENER", "DETENER_INMEDIATO"]:
        res_critico = {
            "estado_self": {"estado": "BURNOUT_INMINENTE"},
            "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
            "coherencia_score": 0.0,
            "decision": {"accion": accion}
        }
        mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, res_critico)
        assert mc == 0.0 and ci == 0.0

def test_guardianes_de_rango():
    """La paradoja del 0.05 y 0.075: la base de la paz."""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
