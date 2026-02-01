import pytest
import time
from villasmil_omega import core, respiro, l2_model

def test_ataque_al_nucleo_core():
    # 1. Protección contra Nulos (Línea 15)
    assert core.indice_mc(None) == 0.0
    
    # 2. Protocolo de Burnout Total (Líneas 32-35)
    # Estructura exacta para forzar el apagado de seguridad
    directiva_hostil = {
        "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
        "decision": {"accion": "DETENER"}
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(0.8, 0.8, directiva_hostil)
    assert mc == 0.0 and ci == 0.0

    # 3. Tensión en clusters pequeños idénticos (Líneas 52-53)
    assert core.compute_theta(["estabilidad", "estabilidad"]) == 0.0

    # 4. Flujo basal sin directiva meta (Línea 95)
    res_basal = core.procesar_flujo_omega([1, 2, 3], {"action": "none"})
    assert res_basal["status"] == "basal"

    # 5. Clamps de actualización L2 (Línea 109)
    # Forzamos que el valor intente ser negativo para activar el 'minimo'
    assert core.actualizar_L2(0.1, delta=-2.0, minimo=0.0) == 0.0

def test_ataque_al_respiro_temporal():
    # Líneas 29-36: El ataque del "Tiempo Congelado"
    # Forzamos que elapsed sea menor a 0.001 para activar la guardia de respiro
    class MockState:
        window_start = time.time() + 1000  # Tiempo en el futuro
        intervention_count = 0
    
    config = respiro.RespiroConfig()
    # Esto debe retornar False por la guardia de tiempo, no por lógica de negocio
    assert respiro.detect_respiro(MockState(), config, 0.01) is False

def test_invariancia_limites_hacker():
    from villasmil_omega.cierre.invariancia import Invariancia
    inv = Invariancia(ventana=5, epsilon=0.01)
    
    # Forzamos Ruptura de Invariancia (Línea 27 del reporte anterior)
    # El sistema debe detectar que el 5.0 rompe la paz
    assert inv.es_invariante([1.0, 1.0, 1.0, 1.0, 5.0]) is False
    
    # Forzamos Ventana Insuficiente (Línea 17)
    assert inv.es_invariante([1.0, 1.0]) is False

def test_l2_model_limites_extremos():
    # Si l2_model tiene clamps de seguridad, aquí los activamos
    # Enviar valores que fuercen el 85% al 100%
    if hasattr(l2_model, 'ajustar_limites'):
        assert l2_model.ajustar_limites(5.0) == 1.0
        assert l2_model.ajustar_limites(-5.0) == 0.0
