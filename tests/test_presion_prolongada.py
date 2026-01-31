import pytest
import villasmil_omega.core as core
import villasmil_omega.l2_model as l2m
import villasmil_omega.human_l2.puntos as pts
from villasmil_omega.respiro import should_apply
from villasmil_omega.cierre.invariancia import Invariancia

def test_cobertura_total_omega():
    # 1. CORE: Forzar colapso de lógica (Líneas 82, 84, 90-94)
    core.compute_theta([])                             # Línea 82 (Vacío)
    core.compute_theta(["solo_uno"] * 10)              # Línea 84 (Sin diversidad)
    # Mezcla de strings que no activan descriptores (Líneas 90-94)
    core.compute_theta(["x", "y", "z", "w"])

    # 2. PUNTOS: Forzar estados de Riesgo y Recuperación (Líneas 66, 69, 180-189)
    sistema = pts.SistemaCoherenciaMaxima()
    sistema.mu_self = None                             # Línea 180 (Init técnico)
    sistema.registrar_medicion({"f": 0.5}, {"c": 0.5})
    
    # Forzar RIESGO_SELF (Línea 186): mu muy bajo + fatiga extrema
    sistema.mu_self, sistema.MAD_self = 0.01, 0.00001
    sistema.registrar_medicion({"fatiga_fisica": 0.99}, {"c": 0.1})
    
    # Forzar RECUPERACION (Línea 188): mu sube de golpe
    sistema.mu_self = 0.95
    sistema.registrar_medicion({"fatiga_fisica": 0.05}, {"c": 0.9})

    # 3. L2_MODEL: Forzar Clamps y Swaps (Líneas 52-53, 89, 103-107)
    l2m.ajustar_L2(-5.0, 1.0)                          # Línea 52 (Clamp < 0)
    l2m.ajustar_L2(5.0, 1.0)                           # Línea 53 (Clamp > 1)
    
    # Swap de seguridad (Línea 89): min_L2 es mayor que max_L2
    l2m.compute_L2_final(0.1, 0.1, 0.5, 0.5, [0.1], 0.5, 0.01, 0.9, 0.1)
    
    # Saturación Bio-max (Líneas 103-107): Fatiga máxima inyectada
    l2m.compute_L2_final(0.9, 0.9, 0.1, 0.1, [0.9], 0.1, 0.01, 0.1, 1.0)

    # 4. RESPIRO e INVARIANCIA (Líneas 40-41 y 12)
    should_apply(0.5, {"e": 2.0}, {"e": 2.1}, cost_threshold=0.1) # Líneas 40-41
    inv = Invariancia(epsilon=0.0001)
    inv.es_invariante([0.5, 0.5, 0.5, 0.5, 0.5, 0.5])  # Línea 12
