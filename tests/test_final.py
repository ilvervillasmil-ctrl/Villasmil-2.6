import pytest
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, indice_mc
from villasmil_omega.respiro import should_apply
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

def test_l2_estadistica_y_reset():
    """Cubre las líneas estadísticas de puntos.py y la rama de historia vacía."""
    # Caso 1: Datos para activar MAD/Sigma
    sistema = SistemaCoherenciaMaxima()
    for i in range(20):
        val = 0.9 if i % 2 == 0 else 0.1
        sistema.registrar_medicion({"f": val}, {"contexto": 1.0 - val})
    assert sistema.get_estado_actual() is not None

    # Caso 2: Sistema nuevo para cubrir 'if not self.history' (Líneas 66, 69)
    sistema_vacio = SistemaCoherenciaMaxima()
    assert sistema_vacio.get_estado_actual() is None

def test_core_resiliencia_protocolos():
    """Cubre las líneas 81-107 de core.py (Estados críticos)."""
    mock_l2 = {
        "estado_self": {"estado": "BLOQUEO"},
        "estado_contexto": {"estado": "CAOS"},
        "coherencia_score": 0.0,
        "decision": {"accion": "STOP"}
    }
    mc, ci = ajustar_mc_ci_por_coherencia(0.8, 0.8, mock_l2)
    assert mc == 0.0
    assert indice_mc(0, 0) == 0.0

def test_respiro_umbral_coste():
    """Cubre las líneas 40-41 de respiro.py."""
    # Forzamos que el coste supere el umbral para que el sistema 'elija' no actuar
    paz, _ = should_apply(0.9, {"L1": 0.5}, {"L1": 0.51}, cost_threshold=0.1)
    assert paz is True

def test_defensa_extrema_core():
    """Cubre las líneas de seguridad 82-94 de core.py activando defensas de tipos."""
    from villasmil_omega.core import ajustar_mc_ci_por_coherencia
    # Pasamos datos incoherentes para activar las líneas de seguridad
    # Al pasar un string donde debe ir un dict/float, el core se protege.
    mc, ci = ajustar_mc_ci_por_coherencia("error", 0.5, None)
    assert mc == 0.0 # El sistema se bloquea por seguridad
