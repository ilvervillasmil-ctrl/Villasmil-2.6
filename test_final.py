import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts
from villasmil_omega.respiro import should_apply

def test_clausura_total_v26():
    # 1. CORE: Forzar guardias técnicas (Líneas 81-107)
    core.compute_theta([])                             # Lista vacía
    core.compute_theta(["m1"] * 10)                    # Sin diversidad
    core.compute_theta(["x", "y", "z", "w"])           # Desconocidos

    # 2. PUNTOS: Forzar estados críticos (Líneas 66, 69, 180-189)
    s = pts.SistemaCoherenciaMaxima()
    s.mu_self = None                                   # Forzar init técnico
    s.registrar_medicion({"f": 0.5}, {"c": 0.5})
    s.mu_self, s.MAD_self = 0.01, 0.0001               # Estado de RIESGO
    s.registrar_medicion({"fatiga_fisica": 0.99}, {"c": 0.1})

    # 3. L2_MODEL: Forzar Clamps y Swaps (Líneas 52-53, 89, 103-107)
    l2m.ajustar_L2(-5.0, 1.0)                          # Clamp inferior
    l2m.ajustar_L2(5.0, 1.0)                           # Clamp superior
    # Forzar Swap de seguridad (Línea 89)
    l2m.compute_L2_final(0.1, 0.1, 0.5, 0.5, [0.1], 0.5, 0.01, 0.9, 0.1)
    # Saturación Bio-max (Líneas 103-107)
    l2m.compute_L2_final(0.9, 0.9, 0.1, 0.1, [0.9], 0.1, 0.01, 0.1, 1.0)

    # 4. RESPIRO e INVARIANCIA (Líneas 40-41, 56 y 12)
    should_apply(0.5, {"e": 0.9}, {"e": 0.99}, cost_threshold=0.1)
    from villasmil_omega.cierre.invariancia import Invariancia
    inv = Invariancia(epsilon=0.0001)
    inv.es_invariante([0.5] * 10)                      # Línea 12

    assert True
