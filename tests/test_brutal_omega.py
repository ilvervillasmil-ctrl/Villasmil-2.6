import pytest
import time
from villasmil_omega import core, respiro, l2_model

def test_core_final_annihilation():
    # 1. Fuerza la línea 15 y 20 (Nulos y vacíos)
    assert core.indice_mc(None) == 0.0
    assert core.indice_mc([]) == 0.0
    
    # 2. Línea 35: Burnout Estricto
    # El diccionario DEBE tener los dos niveles para que .get() no falle antes de la línea
    burnout = {"estado_self": {"estado": "BURNOUT_ABSOLUTO"}, "decision": {"accion": "DETENER"}}
    mc, ci = core.ajustar_mc_ci_por_coherencia(1.0, 1.0, burnout)
    assert mc == 0.0

    # 3. Línea 53: Cluster pequeño idéntico
    assert core.compute_theta(["omega", "omega"]) == 0.0

    # 4. Línea 95: Salto de flujo basal
    assert core.procesar_flujo_omega([1], {"action": "basal"})["status"] == "basal"

def test_respiro_ultra_precision():
    # A. Líneas 35-36: Tiempo Congelado (Guardia de seguridad inicial)
    class FreezeState:
        window_start = time.time() + 10  # En el futuro
    assert respiro.detect_respiro(FreezeState(), {"max_rate": 100}, 0.01) is False

    # B. Línea 50: Tasa Infinita (Sin disparar la guardia de la línea 36)
    # Dejamos pasar 0.1 segundos (más que 0.001) para que no muera en la entrada
    class FastState:
        window_start = time.time() - 0.1 
        intervention_count = 1000  # 1000 intervenciones en 0.1s = 36 millones/hora
    
    assert respiro.detect_respiro(FastState(), {"max_interv_rate": 100}, 0.01) is True

    # C. Línea 67: Similitud L2 (Relajación)
    # Pasamos los argumentos como kwargs para que coincida con la firma mixta
    res = respiro.should_apply(
        current_R=0.5, 
        effort_soft={'L1': 0.5}, 
        effort_hard={'L1': 0.5001}
    )
    # should_apply retorna (bool, str) cuando recibe current_R
    assert res[0] is True 

def test_l2_model_anomalies():
    # Atacamos las zonas ciegas de l2_model (49-50, 92-96)
    # Si estas líneas son validaciones de límites, enviamos extremos
    if hasattr(l2_model, 'actualizar_L2'):
        # Forzar el clamp de suelo (Línea 109 core / l2 logic)
        assert core.actualizar_L2(0.0, delta=-1.0, minimo=0.0) == 0.0
