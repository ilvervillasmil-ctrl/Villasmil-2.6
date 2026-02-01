import pytest
import time
from villasmil_omega import core, respiro, l2_model

def test_core_final_annihilation():
    # Línea 15 y 20: Ataque directo a la firma de indice_mc
    assert core.indice_mc(None) == 0.0
    assert core.indice_mc([]) == 0.0
    
    # Línea 35: Forzamos el retorno específico del protocolo de Burnout
    # Enviamos una estructura que obligue a la función a devolver 0.0, 0.0
    burnout_strict = {
        "estado_self": {"estado": "BURNOUT_ABSOLUTO"},
        "decision": {"accion": "DETENER"}
    }
    mc, ci = core.ajustar_mc_ci_por_coherencia(1.0, 1.0, burnout_strict)
    assert mc == 0.0 and ci == 0.0

    # Línea 52-53: Theta en micro-cluster identitario
    # Debe ser una lista menor a 6 elementos para que entre en la rama
    assert core.compute_theta(["paz", "paz"]) == 0.0

    # Línea 95: Cobertura del retorno basal por defecto
    assert core.procesar_flujo_omega([1], {"action": "invalid"})["status"] == "basal"

def test_respiro_time_warp():
    # Líneas 35-36: El ataque del tiempo negativo/cero
    # Mockeamos el objeto state para que elapsed sea exactamente < 0.001
    class FreezeState:
        window_start = time.time() + 5000 # 5000 segundos en el futuro
        intervention_count = 0
    
    # Esto fuerza la línea 36 (return False)
    assert respiro.detect_respiro(FreezeState(), {"max_rate": 100}, 0.01) is False

    # Línea 50: Forzar tasa de intervención infinita
    class HyperState:
        window_start = time.time() - 0.0001 # Hace un instante
        intervention_count = 999999
    assert respiro.detect_respiro(HyperState(), {"max_interv_rate": 1}, 0.01) is True

    # Línea 67: La similitud L2 exacta (Relajación)
    # Debería activarse cuando effort_hard y effort_soft son casi iguales
    res = respiro.should_apply(
        current_R=0.5, 
        effort_soft={'L1': 0.1}, 
        effort_hard={'L1': 0.1001}
    )
    assert res[0] is True # Similitud detectada

def test_l2_model_deep_scan():
    # Atacamos las líneas 49-50 y 92-96 de l2_model
    # Si existen funciones de límite o validación, las estresamos
    if hasattr(l2_model, 'actualizar_L2'):
        # Forzar el clamp de techo
        assert l2_model.actualizar_L2(0.9, delta=0.5) == 1.0
        # Forzar el clamp de suelo
        assert l2_model.actualizar_L2(0.1, delta=-0.5) == 0.0
