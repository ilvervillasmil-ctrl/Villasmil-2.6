import pytest
import time
from villasmil_omega import core, respiro, l2_model, modulador

def test_ataque_quirurgico_core():
    # Línea 15: Envío de None para forzar guardia de indice_mc
    assert core.indice_mc(None) == 0.0
    
    # Línea 20: Envío de lista vacía para forzar guardia de indice_mc
    assert core.indice_mc([]) == 0.0

    # Líneas 32-35: Inyección de veneno en directiva para forzar Burnout Absoluto
    # Atacamos el motor de decisión para que el flujo muera en el retorno (0.0, 0.0)
    veneno = {
        "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
        "decision": {"accion": "DETENER"}
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(1.0, 1.0, veneno)
    assert mc == 0.0 and ci == 0.0

    # Líneas 52-53: Estabilidad forzada en cluster minúsculo
    # Si la longitud es < 6 y son iguales, debe retornar 0.0
    assert core.compute_theta(["paz", "paz"]) == 0.0

    # Línea 95: Salto de evolución
    # Directiva sin meta_auth ni force_probe
    res = core.procesar_flujo_omega([1, 2, 3], {"ignore": True})
    assert res["status"] == "basal"

def test_ataque_total_respiro():
    # Líneas 29-36: El ataque del "Reloj Roto"
    # Forzamos que el tiempo de inicio sea en el futuro para que elapsed sea negativo
    class MockState:
        window_start = time.time() + 10000 
        intervention_count = 0
    
    # La guardia elapsed < 0.001 DEBE activarse aquí
    assert respiro.detect_respiro(MockState(), {"max_rate": 100}, 0.0) is False

    # Línea 50: Forzar intervención excesiva
    class HighRateState:
        window_start = time.time() - 1 # 1 segundo atrás
        intervention_count = 1000000   # Millones de intervenciones
    assert respiro.detect_respiro(HighRateState(), {"max_interv_rate": 1}, 0.0) is True

def test_ataque_l2_y_modulador():
    # l2_model: Líneas 49-50 y 92-96 (Clamps y errores)
    # Intentamos romper el modelo L2 con valores fuera de escala
    if hasattr(l2_model, 'actualizar'):
        assert l2_model.actualizar(2.0) <= 1.0 # Techo
        assert l2_model.actualizar(-2.0) >= 0.0 # Suelo

    # modulador: Líneas 34-35 y 43 (Fallas de entrada)
    if hasattr(modulador, 'modular'):
        # Enviamos datos basura al modulador
        assert modulador.modular(None, -1) is not None

def test_limite_fisico_final():
    # Línea 109 del core: El clamp final de actualizar_L2
    # Forzamos que baje de cero
    assert core.actualizar_L2(0.0, delta=-1.0, minimo=0.0) == 0.0
