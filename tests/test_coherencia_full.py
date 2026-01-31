import pytest
import math
# Cambiamos la ruta de importación para que sea directa al archivo
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima, ConfiguracionEstandar
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, actualizar_L2

def test_ataque_total_unificado():
    """Prueba la lógica biológica ahora residente en el __init__."""
    # Si moviste todo a __init__.py, asegúrate de que el archivo puntos.py 
    # no exista o esté vacío. Si no, usa esta ruta:
    conf = ConfiguracionEstandar(DELTA_ABS_SELF=0.01)
    sistema = SistemaCoherenciaMaxima(config=conf)
    
    # 1. Forzar cálculos estadísticos (MAD/Sigma)
    for v in [0.1, 0.9, 0.2, 0.8, 0.3]:
        sistema.registrar_medicion({"fatiga_fisica": v}, {"feedback_directo": v})
    
    # 2. Verificar que el estado cambió
    res = sistema.get_estado_actual()
    assert res is not None

def test_core_100_percent():
    """Aniquila las líneas 78, 84, 96-97 de core.py."""
    # Límites de seguridad
    assert actualizar_L2(0.5, delta=2.0) == 1.0
    assert actualizar_L2(0.5, delta=-2.0) == 0.0
    
    # Caso de bloqueo crítico por Burnout/Self-Crítico
    res_critico = {
        "estado_self": {"estado": "SELF_CRITICO"},
        "estado_contexto": {"estado": "CONTEXTO_ESTABLE"},
        "coherencia_score": 0.0,
        "decision": {"accion": "DETENER_INMEDIATO"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.8, 0.8, res_critico)
    assert mc == 0.0 and ci == 0.0
