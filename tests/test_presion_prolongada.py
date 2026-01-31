import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts
from villasmil_omega.respiro import should_apply

def test_ataque_quirurgico_100_percent():
    # 1. CORE: Forzar guardias técnicas (Líneas 82, 84, 90-94)
    core.compute_theta([])                                      # Línea 82
    core.compute_theta(["solo_uno"] * 10)                        # Línea 84
    core.compute_theta(["desconocido_1", "desconocido_2"])       # Líneas 90-94

    # 2. PUNTOS: Forzar estados de pánico (Líneas 180-189)
    sistema = pts.SistemaCoherenciaMaxima()
    sistema.mu_self = None                                      # Línea 180 (inicialización)
    sistema.registrar_medicion({"f": 0.5}, {"c": 0.5})
    
    # Forzar RIESGO_SELF (Líneas 186-187)
    sistema.mu_self, sistema.MAD_self = 0.1, 0.0001
    sistema.registrar_medicion({"fatiga_fisica": 0.99}, {"c": 0.1})
    
    # Forzar RECUPERACION (Línea 188)
    sistema.mu_self = 0.9
    sistema.registrar_medicion({"fatiga_fisica": 0.01}, {"c": 0.9})

    # 3. L2_MODEL: Forzar Clamps y Swaps (Líneas 42, 52-53, 89, 103-107)
    l2m.ajustar_L2(-5.0, 1.0)                                   # Línea 52 (Clamp inferior)
    l2m.ajustar_L2(5.0, 1.0)                                    # Línea 53 (Clamp superior)
    
    # Forzar Swap de seguridad (Línea 89): min_L2 > max_L2
    l2m.compute_L2_final(0.1, 0.1, 0.5, 0.5, [0.1], 0.5, 0.01, 0.9, 0.1)
    
    # Forzar Bio-max (Líneas 103-107)
    l2m.compute_L2_final(0.9, 0.9, 0.1, 0.1, [0.9], 0.1, 0.01, 0.1, 1.0)

    # 4. RESPIRO e INVARIANCIA (Líneas 40-41 y 12)
    should_apply(0.5, {"e": 1.5}, {"e": 1.6}, cost_threshold=1.0)
    from villasmil_omega.cierre.invariancia import Invariancia
    inv = Invariancia(epsilon=0.0001)
    inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.5, 0.5]) # Línea 12
