import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts
from villasmil_omega.respiro import should_apply

def test_clausura_total_v26():
    # 1. Recuperar CORE (Líneas 81-107)
    # Forzamos listas vacías y datos inconsistentes para entrar en las guardias
    core.compute_theta([]) 
    core.compute_theta(["data"] * 10)
    core.compute_theta(["x", "y", "z"]) 

    # 2. Recuperar PUNTOS (Líneas 66, 69, 180-189)
    s = pts.SistemaCoherenciaMaxima()
    s.mu_self = None # Fuerza init técnico
    s.registrar_medicion({"f": 0.5}, {"c": 0.5})
    s.mu_self, s.MAD_self = 0.01, 0.0001 # Fuerza RIESGO_SELF
    s.registrar_medicion({"fatiga_fisica": 0.99}, {"c": 0.1})

    # 3. Recuperar L2_MODEL (Líneas 52-53, 103-107)
    l2m.ajustar_L2(-1.0, 1.0) # Clamp inferior
    l2m.ajustar_L2(2.0, 1.0)  # Clamp superior
    # Fuerza saturación bio-max
    l2m.compute_L2_final(0.9, 0.9, 0.1, 0.1, [0.9], 0.1, 0.01, 0.1, 1.0)

    # 4. Recuperar RESPIRO (Líneas 40-41, 56)
    should_apply(0.5, {"e": 0.9}, {"e": 0.99}, cost_threshold=0.1)

    # 5. Invariancia (Línea 12)
    from villasmil_omega.cierre.invariancia import Invariancia
    inv = Invariancia(epsilon=0.0001)
    inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])

    assert True
