import pytest
from villasmil_omega.core import ajustar_mc_ci_por_coherencia
from villasmil_omega.human_l2.puntos import (
    SistemaCoherenciaMaxima, 
    ConfiguracionEstandar,
    compute_L2_self,
    compute_L2_contexto
)

def test_presion_y_compensacion():
    """Al apretar la coherencia en L2, la presión debe subir en Core."""
    sistema = SistemaCoherenciaMaxima()
    
    # 1. ESTABILIZAR L2 (Puntos.py 131-144): 
    # Forzamos una ráfaga que sature los cálculos estadísticos.
    for i in range(15):
        val = 0.1 if i % 2 == 0 else 0.9
        sistema.registrar_medicion({"f": val}, {"e": 1.0 - val})

    # 2. APRETAR CORE (Core.py 74-94):
    # Inyectamos manualmente los estados que faltan en el reporte.
    estados_emergencia = [
        "TENSION_ALTA", "RIESGO_SELF", "SELF_CRITICO", "BURNOUT_INMINENTE"
    ]
    
    for est in estados_emergencia:
        # Si apretamos con este estado...
        res_critico = {
            "estado_self": {"estado": est},
            "estado_contexto": {"estado": "DAÑANDO_CONTEXTO"},
            "coherencia_score": 0.1,
            "decision": {"accion": "CONTINUAR" if est != "BURNOUT_INMINENTE" else "DETENER_INMEDIATO"}
        }
        # ...la lógica en Core.py debe compensar (subir/bajar MC y CI).
        mc, ci = ajustar_mc_ci_por_coherencia(0.8, 0.8, res_critico)
        assert mc < 0.8 or mc == 0.0 # El sistema reaccionó

def test_puntos_muertos_limpieza():
    """Limpia las líneas sueltas 66, 69, 281."""
    assert compute_L2_self({}) == 0.05
    assert compute_L2_contexto({}) == 0.075
    # Historial vacío (línea 281)
    sis = SistemaCoherenciaMaxima()
    sis.history = []
    assert sis.get_estado_actual() is None
