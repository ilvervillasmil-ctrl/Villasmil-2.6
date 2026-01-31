import pytest
import time
from villasmil_omega.respiro import (
    distribute_action,
    RespiroConfig,
    RespiroState,
    should_apply,
    detect_respiro
)
from villasmil_omega.core import ajustar_mc_ci_por_coherencia

def test_l1_sostiene_la_carga():
    """REGLA 1: La L1 distribuye, no reacciona."""
    cfg = RespiroConfig()
    sensitividades = {"L1": 0.1, "L4": 0.9, "L6": 1.0}
    
    # Aplicamos carga pesada
    accion = distribute_action(0.8, sensitividades, cfg)
    
    # Verificamos que L1 sea 'como si nada' (carga mínima)
    assert accion["L1"] < 0.1
    # Verificamos que las capas superiores absorban el esfuerzo
    assert accion["L6"] > accion["L1"]

def test_l2_no_conforme_y_respiro():
    """REGLA 2 y 3: Evaluar si hace falta empujar más."""
    # Simulamos que ya estamos cerca del objetivo
    # (Mente relajada: ganancia marginal pequeña)
    apply_soft, marginal = should_apply(
        current_R=0.9,
        effort_soft={"L1": 0.05},
        effort_hard={"L1": 0.5},
        cost_threshold=1.0
    )
    
    # Si la ganancia es mínima, apply_soft debe ser True (no hace falta empujar)
    assert apply_soft is True
    
    # Validamos el estado de Respiro (Éxito = No reaccionar)
    st = RespiroState()
    st.window_start = time.time() - 3600
    st.deadband_seconds = 3000
    st.interv_count = 1
    
    assert detect_respiro(st, cfg=RespiroConfig(), marginal_gain_probe=0.01) is True

def test_apretar_aqui_para_subir_alla():
    """Conectamos el Respiro con los 'Missings' de Core (81-107)."""
    # Forzamos los estados de colapso que faltan en el reporte
    for estado in ["BLOQUEO", "DETENER_INMEDIATO", "BURNOUT_INMINENTE"]:
        mock_l2 = {
            "estado_self": {"estado": estado},
            "estado_contexto": {"estado": "CAOS"},
            "coherencia_score": 0.0,
            "decision": {"accion": "BLOQUEO" if estado == "BLOQUEO" else "DETENER_INMEDIATO"}
        }
        # Esta llamada 'ilumina' las líneas 81-107 de core.py
        mc, ci = ajustar_mc_ci_por_coherencia(0.5, 0.5, mock_l2)
        assert mc == 0.0
