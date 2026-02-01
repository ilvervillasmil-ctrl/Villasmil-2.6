import pytest
import time
from villasmil_omega import core, l2_model, respiro
from villasmil_omega.cierre.invariancia import Invariancia

def test_ataque_corrupcion_datos_core():
    """Ataca compute_theta con tipos de datos hostiles."""
    # Forzamos fallo de tipos para activar el except (si lo hay) o ramas de error
    assert core.compute_theta([None, 123, "unknown", 0.0001]) >= 0
    # Forzamos cluster pequeño con identidad total (Líneas 52-53)
    assert core.compute_theta(["paz"] * 3) == 0.0

def test_ataque_invariancia_caotica():
    """Ataca la invarianza para forzar el reporte de 'Ruptura'."""
    inv = Invariancia(ventana=5, epsilon=0.001)
    # 1. Ventana insuficiente (Línea 17)
    assert inv.es_invariante([1.0, 1.0]) is False
    # 2. Ruptura brusca / Caos (Línea 27)
    assert inv.es_invariante([1.0, 1.0, 1.0, 1.0, 5.0]) is False

def test_ataque_burnout_l2():
    """Fuerza al sistema al estado de Burnout absoluto."""
    mc, ci = core.ajustar_mc_ci_por_coherencia(
        0.9, 0.9, 
        {"estado_self": {"estado": "BURNOUT_ABSOLUTO"}, "decision": {"accion": "DETENER"}}
    )
    assert mc == 0.0 and ci == 0.0

def test_estres_respiro_division_cero():
    """Ataca el motor de respiro con micro-tiempos."""
    state = respiro.RespiroState()
    config = respiro.RespiroConfig()
    # Forzamos un tiempo transcurrido casi nulo (Línea 29-36)
    state.window_start = time.time() + 100 # Tiempo en el futuro o idéntico
    assert respiro.detect_respiro(state, config, 0.01) is False

def test_limites_fisicos_l2():
    """Ataca los clamps de L2 con valores fuera de la realidad."""
    # Forzamos el techo de OMEGA_U
    assert core.suma_omega(0.9, 0.2) == 0.995
    # Forzamos clamps de actualizar_L2 (Líneas 109 y más)
    assert core.actualizar_L2(0.1, delta=-5.0) == 0.0
    assert core.actualizar_L2(0.9, delta=5.0) == 1.0
