import pytest
import villasmil_omega.core as core
from villasmil_omega.l2_model import ajustar_L2, compute_L2_final
from villasmil_omega.human_l2.puntos import SistemaCoherenciaMaxima

def test_cobertura_absoluta_omega():
    # --- 1. CORE (Líneas 82, 84, 90-91, 93-94) ---
    core.compute_theta([]) 
    core.compute_theta(["model a"] * 10)
    core.compute_theta(["model a text"] * 3 + ["model b text"] * 3)

    # --- 2. L2_MODEL (Líneas 42, 52-53, 89, 103-107) ---
    ajustar_L2(-1.0, 1.0)
    ajustar_L2(2.0, 1.0)
    # Forzar el swap de seguridad (min > max) y saturación bio_max
    compute_L2_final(0.1, 0.1, 0.5, 0.5, [0.25], 0.25, 1.0, 0.9, 0.1)

    # --- 3. PUNTOS (Líneas 66, 69, 180-189) ---
    sistema = SistemaCoherenciaMaxima()
    sistema.mu_self = None # Fuerza inicialización (180)
    sistema.registrar_medicion({"f": 0.5}, {"f": 0.5})
    # Forzar Riesgo (186) y Recuperación (188)
    sistema.mu_self, sistema.MAD_self = 0.1, 0.001
    sistema.registrar_medicion({"fatiga_fisica": 0.9}, {"f": 0.5})
    sistema.mu_self = 0.9
    sistema.registrar_medicion({"fatiga_fisica": 0.1}, {"f": 0.5})

    # --- 4. RESPIRO E INVARIANCIA (40-41, 12) ---
    from villasmil_omega.respiro import should_apply
    from villasmil_omega.cierre.invariancia import Invariancia
    should_apply(0.5, {"e": 1.5}, {"e": 1.6}, cost_threshold=1.0)
    Invariancia(epsilon=0.001).es_invariante([0.5, 0.5, 0.502])
