import pytest
import math
from villasmil_omega.core import ajustar_mc_ci_por_coherencia, indice_mc
from villasmil_omega.respiro import should_apply
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

# 1. ATAQUE AL CORE: Protocolos de Emergencia (Líneas 81-107)
def test_protocolos_emergencia_core():
    """Fuerza al core a reconocer estados de colapso real."""
    estados_criticos = ["BLOQUEO", "DETENER_INMEDIATO", "BURNOUT_INMINENTE"]
    for estado in estados_criticos:
        mock_l2 = {
            "estado_self": {"estado": estado},
            "estado_contexto": {"estado": "CAOS_TOTAL"},
            "coherencia_score": 0.0,
            "decision": {"accion": "STOP"}
        }
        # Esto ilumina las ramas de penalización extrema en core.py
        mc, ci = ajustar_mc_ci_por_coherencia(0.9, 0.9, mock_l2)
        assert mc < 0.5 
    
    # Protección división por cero
    assert indice_mc(0, 0) == 0.0

# 2. ATAQUE A PUNTOS: MAD, Sigma y Limpieza (131-247)
def test_l2_estadistica_extrema():
    """Obliga a la L2 a procesar ruido, desviaciones y reseteos."""
    sistema = SistemaCoherenciaMaxima()
    
    # Generamos una ráfaga de datos incoherentes para activar MAD y Sigma
    for i in range(50):
        val = 0.99 if i % 2 == 0 else 0.01
        sistema.registrar_medicion({"f": val}, {"contexto": 1.0 - val})
    
    # Forzamos limpieza de historia (líneas de missing en puntos.py)
    sistema.historial = [] 
    assert sistema.get_estado_actual() is None

# 3. ATAQUE AL RESPIRO: El "No Hacer" (40-41)
def test_sabiduria_del_no_hacer():
    """Activa la rama donde el sistema elige NO actuar por ineficiencia."""
    # current_R alto, esfuerzo alto, pero ganancia marginal nula
    # Esto fuerza la entrada en las líneas 40-41 de respiro.py
    apply_soft, _ = should_apply(
        current_R=0.95,
        effort_soft={"L1": 0.5},
        effort_hard={"L1": 0.51}, 
        cost_threshold=0.1 # Coste soft (0.25) > threshold
    )
    assert apply_soft is True # "Elegir el respiro"

# 4. INVARIANZA: El guard check de la línea 12
def test_invariancia_limite():
    from villasmil_omega.cierre.invariancia import Invariancia
    inv = Invariancia(ventana=5)
    # Lista corta para activar el guard clause inicial (línea 12)
    assert inv.es_invariante([1.0, 1.0]) is False
